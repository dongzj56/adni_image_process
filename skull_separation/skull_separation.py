import os
import nibabel as nib
import numpy as np

# 定义输入和输出目录
input_image_dir = rf'C:\Users\dongz\Desktop\sp\original'
input_mask_dir = rf'C:\Users\dongz\Desktop\sp\p0mask'
output_dir = rf'C:\Users\dongz\Desktop\sp\output'

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

            # 结合蒙版序列和原始图像序列，生成输出图像序列
            output_sequence = original_image * mask_sequence

            # 保存输出图像序列
            output_image = nib.Nifti1Image(output_sequence, affine=orig_nii.affine)
            output_filename = os.path.join(output_dir, image_filename.replace('.nii', '_output.nii.gz'))
            nib.save(output_image, output_filename)
            print(f"Processed and saved: {output_filename}")
        else:
            print(f"Mask not found for: {image_filename}")