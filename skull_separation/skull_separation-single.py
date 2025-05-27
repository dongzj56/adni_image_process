from nibabel.viewers import OrthoSlicer3D
import nibabel as nib
import numpy as np

# 加载原始图像序列
orig_nii = nib.load('测试数据/002_S_4213.nii')
original_image = nib.load('测试数据/002_S_4213.nii').get_fdata()

# 加载蒙版序列
mask_sequence = nib.load('测试数据/p0002_S_4213.nii').get_fdata()

# 结合蒙版序列和原始图像序列，生成输出图像序列
output_sequence = original_image * mask_sequence

# 保存输出图像序列
output_image = nib.Nifti1Image(output_sequence, affine=orig_nii.affine)
nib.save(output_image, 'path_to_output_image.nii.gz')
