import os
import nibabel as nib
import numpy as np

# 定义输入和输出目录
input_image_dir = rf'C:\Users\dongz\Desktop\mask\original'
input_mask_dir = rf'C:\Users\dongz\Desktop\mask\mri'
output_dir = rf'C:\Users\dongz\Desktop\mask\output-2'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 遍历原始图像目录
for image_filename in os.listdir(input_image_dir):
    if image_filename.endswith('.nii'):
        # 加载原始图像
        orig_nii = nib.load(os.path.join(input_image_dir, image_filename))
        original_image = orig_nii.get_fdata()

        # 构建对应的蒙版文件名
        mask_filename = 'p0' + image_filename.replace('原始图像', '蒙版序列')
        mask_path = os.path.join(input_mask_dir, mask_filename)

        # 检查蒙版文件是否存在
        if os.path.exists(mask_path):
            # 加载蒙版序列
            mask_sequence = nib.load(mask_path).get_fdata()

            import numpy as np
            import scipy.ndimage as ndi

            # 1. 阈值得到布尔掩膜（True/False）
            mask_bool = mask_sequence > 0.15          # bool 类型

            # # 2. 开运算：先腐蚀后膨胀，去除毛刺和孤立点
            # mask_bool = ndi.binary_opening(mask_bool, structure=np.ones((3,3,3)), iterations=1)

            # # （可选）再做一次 binary_closing 填小孔
            # mask_bool = ndi.binary_closing(mask_bool, structure=np.ones((3,3,3)), iterations=1)

            # （可选）仅保留最大连通域，防止头皮碎片
            # labeled, _ = ndi.label(mask_bool)
            # largest = np.argmax(np.bincount(labeled.ravel())[1:]) + 1
            # mask_bool = labeled == largest

            # 3. 乘回原图
            output_sequence = original_image * mask_bool.astype(original_image.dtype)



            # 保存输出图像序列
            output_image = nib.Nifti1Image(output_sequence, affine=orig_nii.affine)
            output_filename = os.path.join(output_dir, image_filename.replace('.nii', '_output.nii.gz'))
            nib.save(output_image, output_filename)
            print(f"Processed and saved: {output_filename}")
        else:
            print(f"Mask not found for: {image_filename}")