'''按照体素调整图像大小'''
import nibabel as nib
import numpy as np
from scipy.ndimage import zoom
import os

def resample_nifti(input_path, output_path, new_voxel_size):
    """
    读取NIfTI影像，按照新的体素大小进行重采样，并保存新的影像文件。

    参数:
    - input_path: 原始NIfTI文件路径
    - output_path: 重采样后保存的NIfTI文件路径
    - new_voxel_size: 新的体素大小，格式为(tuple) (vx, vy, vz) 单位为毫米
    """
    # 1. 读取原始影像
    img = nib.load(input_path)
    data = img.get_fdata()
    affine = img.affine.copy()
    header = img.header.copy()

    # 2. 获取原始 Size 和 Voxel Size
    orig_shape = data.shape
    orig_voxel_size = header.get_zooms()[:3]
    print(f"处理文件: {os.path.basename(input_path)}")
    print("原始 Size:", orig_shape)
    print("原始 Voxel Size:", orig_voxel_size)

    # 3. 计算每个方向的缩放因子
    scale_factors = tuple(orig_voxel_size[i] / new_voxel_size[i] for i in range(3))

    # 4. 执行重采样（双线性插值）
    resampled_data = zoom(data, scale_factors, order=1)

    # 5. 计算新的 Size
    new_shape = resampled_data.shape

    # 6. 构建新的 affine（仅修改对角线的 voxel 大小部分）
    new_affine = affine.copy()
    for i in range(3):
        new_affine[i, i] = new_voxel_size[i]

    # 7. 更新 header 中的体素大小
    new_header = header.copy()
    new_header.set_zooms(new_voxel_size)

    # 8. 保存新的 NIfTI 影像
    new_img = nib.Nifti1Image(resampled_data, new_affine, header=new_header)
    nib.save(new_img, output_path)

    # 9. 输出结果
    print("重采样后 Size:", new_shape)
    print("新的 Voxel Size:", new_voxel_size)
    print(f"已保存到: {output_path}\n")


def process_directory(input_dir, output_dir, new_voxel_size):
    """
    处理指定目录下的所有NIfTI文件
    
    参数:
    - input_dir: 输入目录路径
    - output_dir: 输出目录路径
    - new_voxel_size: 新的体素大小
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
    
    # 获取所有NIfTI文件
    nifti_files = [f for f in os.listdir(input_dir) if f.endswith(('.nii', '.nii.gz'))]
    
    if not nifti_files:
        print(f"在 {input_dir} 中没有找到NIfTI文件(.nii或.nii.gz)")
        return
    
    print(f"找到 {len(nifti_files)} 个NIfTI文件")
    
    # 处理每个文件
    for filename in nifti_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            resample_nifti(input_path, output_path, new_voxel_size)
        except Exception as e:
            print(f"处理 {filename} 时出错: {e}")
    
    print("所有文件处理完成!")


if __name__ == "__main__":
    # 从用户获取输入
    input_dir = input("请输入包含NIfTI文件的目录路径: ")
    output_dir = input("请输入重采样后文件的保存目录: ")
    
    # 设置目标体素大小
    new_voxel_size = (2, 2, 2)  # 默认目标体素大小
    
    # 处理目录中的所有文件
    process_directory(input_dir, output_dir, new_voxel_size)