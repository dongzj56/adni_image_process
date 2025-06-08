'''获取目录下图像大小和体素'''
import os
import nibabel as nib
import pydicom

def get_image_size_and_voxel(image_path):
    """
    获取影像的尺寸和体素大小，支持 NIfTI 和 DICOM 文件。
    """
    if image_path.endswith('.nii') or image_path.endswith('.nii.gz'):
        # 读取NIfTI图像
        img = nib.load(image_path)
        size = img.shape  # 图像尺寸 (depth, height, width)
        voxel_size = img.header.get_zooms()  # 获取体素大小 (voxel size)
        return size, voxel_size
    
    elif image_path.endswith('.dcm'):
        # 读取DICOM图像
        ds = pydicom.dcmread(image_path)
        size = (ds.Rows, ds.Columns)  # 返回 DICOM 图像的尺寸 (height, width)
        
        # 对于3D DICOM图像，获取体素大小
        if 'SpacingBetweenSlices' in ds and 'PixelSpacing' in ds:
            voxel_size = (ds.PixelSpacing[0], ds.PixelSpacing[1], ds.SpacingBetweenSlices)
        else:
            voxel_size = None
        
        return size, voxel_size
    
    else:
        return None, None

def print_image_sizes_and_voxels(directory):
    """
    遍历目录并打印所有影像文件的尺寸和体素大小
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.nii') or file.endswith('.nii.gz') or file.endswith('.dcm'):
                size, voxel_size = get_image_size_and_voxel(file_path)
                if size:
                    voxel_info = f"Voxel Size: {voxel_size}" if voxel_size else "Voxel Size: N/A"
                    print(f"File: {file_path} | Size: {size} | {voxel_info}")
                else:
                    print(f"File: {file_path} | Unsupported file format")

# 示例目录路径
<<<<<<< Updated upstream
<<<<<<< Updated upstream
directory = rf'C:\Users\dongzj\Desktop\TEST\MRI'
=======
directory = rf'C:\Users\dongz\Desktop\test'
>>>>>>> Stashed changes
=======
directory = rf'F:\ADNI数据集902样本\05-mask处理后全脑图像\MRI_MNI_193_229_193'
>>>>>>> Stashed changes

# 打印所有影像文件的尺寸和体素大小
print_image_sizes_and_voxels(directory)
