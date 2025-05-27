# ADNI影像数据预处理说明

# MRI处理流程

## 第一步 数据格式转换
### 1 转换(.dcm)文件为(.nii)格式
运行`dcm2nii_all.py`可以批量处理ADNI影像数据下载目录中的dcm文件，转为nii格式保存。运行此代码，dcm文件不会删除。

修改`root_dir = r'C:\Users\dongz\Desktop\ADNI_Image_MRI\ADNI'`为影像下载路径后运行。
修改`dcm2niix_path = r'tools\dcm2niix.exe'`为自己的路径。

dcm2niix.exe可前往`https://github.com/rordenlab/dcm2niix/releases`下载，或是在mricron软件resources下查找。
### 2 修改数据集存储格式，方便后续调用
运行`datapath_modif.py`可以更改数据集存储结构，方便后续的数据预处理和模型训练。这个代码不是必须的，可以根据需要选择是否运行。

修改代码中`root_dir = r"C:\Users\dongz\Desktop\ADNI_Image_MRI\ADNI"`为影像下载路径即可。

###### 数据集结构

```plaintext
.
├── MRI/                    # MRI数据
│   ├── 002_S_2010.nii
│   ├── 002_S_2043.nii
│   └── ...
├── PET/                    # PET数据
│   ├── 002_S_2010.nii
│   ├── 002_S_2043.nii
│   └── ...
|——table/                   # 非影像数据
|   |——cognitive_test
|   |——Biomarkers_test
|   └──...
└── train_label.csv                # 标签
```

## 第二步 AC-PC校正

将图像的坐标原点设置到AC-PC连线，方便后续的配准。
Matlab上有广泛使用的神经影像工具包SPM（需进行配置），集成了AC-PC校正功能。

### 1 手动校正
可以使用 SPM 或 ITK-SNAP 进行手动校正

### 2 批量校正
参考`https://github.com/CyclotronResearchCentre/spm_auto_reorient`的批量校正代码`spm_auto_reorient.m`，配置好cfg文件运行即可。

运行`spm_auto_reorient.m`文件会报错，直接修改原来的批量处理代码为`Reorient.m`，推荐使用这个。

修改代码：`i_type = 't1'`，可以对T1加权的MRI影像进行AC-PC校正，
`i_type = 'pet'`可对PET影像进行校正，其他影像修改相应参数即可。

1. MRI和PET影像需要单独处理，校正后的文件直接覆盖原文件，需要提前备份原文件。

2. 运行代码生成的temp.nii，会自动删除，如果没有删除，一定手动删除后再运行。

3. 如果AC位置偏离太远，模板匹配不上会报错：`There is not enough overlap in the images to obtain a solution.`，对报错的nii文件，需要先使用MRICron或SPM手动校正到大概位置再批量处理。

在`Reorient.m`中，修改了`center_origin=true`，会直接先将影像的ac点设置在中心位置，这样设置后都能匹配上。

另外，也提供使用`Python`进行AC-PC校正的代码`ac_pc.py`，但是校正效果尚未进行比较验证。

### MRI影像AC-PC校正前后对比

左侧为原图，右侧为AC-PC校正后

###### 941_S_4377
![这是图片](img\ADNI_941_S_4377_original.png "Magic Gardens")![这是图片](img\ADNI_941_S_4377_acpc.png "Magic Gardens")

###### 941_S_4764
![这是图片](img\ADNI_941_S_4764_original.png "Magic Gardens")![这是图片](img\ADNI_941_S_4764_acpc.png "Magic Gardens")

## 第三步 偏置校正和空间配准

MRI成像时，由于磁场不均匀或射频线圈灵敏度差异，同一组织在不同位置的信号强度会不一致（如脑灰质在图像中心更亮，边缘更暗）。这种亮度不均匀性会干扰后续分析（如组织分割、定量测量），因此需要进行N3或N4校正。

### 1 N4校正
运行`N4_Bias_correction.py`可以进行N4校正

这一步可以跳过，因为后面MRI颅骨分离可以选择进行偏置校正，并会配准（使用aal3模板）。

如果从ADNI下载的是预处理后的影像，一般都进行了N3偏置校正，可以自行检查对部分影像进行N4校正。

### 2 配准
提供批量配准的代码：`batch_coregister_mri.m`，颅骨分离时可以选择同时进行配准，所以这一步也可以跳过。

## 第四步 MRI颅骨分离

使用Matlab集成的cat12进行颅骨分离，并将脑组织分割为灰质、白质、脑脊液。

###### 注意

可以在MRI颅骨分离前，使用SPM12选择模板进行配准，但是对数据预处理结果影响不大，因为使用cat12进行颅骨分离时会自动进行空间配准，由原始空间配准到MNI标准空间

### 1 使用cat12进行颅骨分离
在cat12中选择segment，修改如下参数

###### 参数1
修改`own atlas maps`为`spm12\toolbox\cat12\templates_MNI152NLin2009cAsym`目录下的aal3.nii模板
###### 参数2
`Surface and thickness estimation`是大脑皮层数据，如果不需要可以选择`No`
###### 参数3
`Deformation Fields`选择`iverse+forward`，或者只选择`forward`，表示将个体影像配准到标准模板。如果需要分脑区结果，可以选择`reverse`，可以将模板脑区标签反向映射回个体影像上。
###### 参数4
`PVE label image in native space`选择`Yes`，
###### 参数5
`Normalized`选择`Yes`，可以进行偏置场校正。

颅骨分离生成的y开头的文件是原始空间到标准空间的映射参数，不要删除，后面用来配准PET影像。

`skull_separation.py`可以利用头骨分离结果中的掩码，对原始图像进行分割，得到去除头骨的大脑影像。（分割后可以再次配准）

# PET处理流程

不是所有的MRI影像都有对应的PET模态数据，需要筛选（ADNI1-3数据集中大约有1251个受试者MRI和PET模态数据都有）

## 第一步 格式转换
与MRI影像处理步骤相同

## 第二步 4D PET转3D 
PEI影像为4D，带有多个时间切片，需要先转为3D再处理，提供批量处理代码：`Main_Fun_Split_4DTo3D.m`，只需要修改路径和切片数量就可以实现4D转3D。

4D PET数据，都是至少有两层，另外有197张4D PET影像有六层，为了尽可能多利用数据，都将分割下的第一层作为由4D转换的3D影像。

## 第三步 AC-PC校正
与MRI影像处理步骤相同，代码中对应的参数`i_type = 'pet'`需要修改，不然会以MRI模板进行校正。

## 第四步 配准到MRI

批量处理脚本：`batch_coregister_pet.m`，更改路径参数，参考图像为分割后的MRI

1. 设置`outputPrefix = 'wr'`，表示既进行normalise偏置场校正，又进行配准，如果不需要校正，设置为`outputPrefix = 'r'`即可。

2. 设置参数`interp = 1`，在变换时使用线性插值，计算速度快。这里考虑到PET分辨率比较低，使用线性插值就行。也可以设置`interp`为4~7，使用高阶插值，结果会更平滑。

在对MRI进行颅骨分离时，生成了y开头的文件，是由原始空间到MNI标准空间的变换参数，可以直接使用这个参数对PET影像进行normalise。在配准脚本中调用了`normalise_job.m`代码就是实现这一功能。

调用时需要修改`normalise_job.m`中的两个参数：

1. Bounding box参数：输出PET图像的体素数量，也就是图像尺寸，我设置的`bb = [-100 -130 -90;100 90 105]`，可以多测试几张PET图像选择合适的参数。
2. vox size参数：体素大小，大多数论文都是[1 1 1]或[2 2 2]，由于使用的aal模板本身体素大小是1，所以设置`vox = [1 1 1]`。


###### 002_S_2010配准前后对比
![这是图片](img\002_S_2010.png "Magic Gardens")![这是图片](img\wr002_S_2010.png "Magic Gardens")

## 第五步 PET计算ROI平均强度
如果使用三维卷积直接提取特征，可以忽略这一步，可以对比一下二者效果差异。

### 1 原理说明
PET影像的体素大小（Voxel size）= 1×1×1 mm³，每个体素的值表示放射性摄取强度（例如 SUV 值）

如果要计算某一个脑区的值，只需要在aal3模板中找到该脑区的索引，然后计算索引对应位置的平均像素值，就可以作为反映摄取强度的特征，即代谢特征。

### 2 计算前调整 

打开配准并标准化的PET图像（wr开头），同时加载aal3模板，可以看到二者能够完全重叠，如下两张影像所示：

![这是图片](img\aal+2010.png "Magic Gardens") ![这是图片](img\aal+2043.png "Magic Gardens")


但是在计算时发现配准后的PEI影像和aal3模板的尺寸、坐标原点都不一样，并不能直接计算对应aal脑区位置的数值，需要进行调整。

如下图中，左侧为配准的PET影像，MNI标准空间坐标原点对应位置为（101，131，91），图像维度为201×221×196；而all3坐标原点为（81，117，73），图像维度为161×197×161。

![这是图片](img\wr002_S_2010_mat.png "Magic Gardens") ![这是图片](img\aal3.png "Magic Gardens")

之所以不同尺寸、不同坐标原点的影像能对应，是因为配准时体素坐标到 MNI 坐标会有一个变换矩阵affine，能将体素坐标转换为MNI坐标，因此不同维度图像可以匹配。

公式：MNI_cor = affine *[𝑥,𝑦,𝑧,1]𝑇，xyz 代表体素在本身数据矩阵的坐标。

按照上述原理，就可以使用SPM的reslice功能改变aal3的大小，为小的aal填充黑边，为大的aal削减黑边，实现坐标对齐，并且这一调整不会影像PET影像本身。运行`Reslice_ROI.m`可以生成适配PET大小的aal3模板：`Reslice_aal3.nii`，然后再用新的脑区模板去计算。

### 3 计算特征值
代码`PET_Intensity.py`可以计算各个脑区的特征值，修改如下参数：

1. ROI=修正大小的aal模板
2. PET=PET影像的路径
3. prefix='wr'，与PET配准时对应
4. subject_Info是下载影像的csv文件，里面有对应受试者的信息
5. roi_csv存储ROI计算结果的文件

