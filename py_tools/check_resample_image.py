'''重采样前后数据质量检查'''
import os
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

def check_image_properties(image_path):
    """检查影像元数据"""
    image = sitk.ReadImage(image_path)
    print(f"File: {os.path.basename(image_path)}")
    print(f"Origin: {image.GetOrigin()}")
    print(f"Direction: {image.GetDirection()}")
    print(f"Spacing: {image.GetSpacing()}")
    print(f"Size: {image.GetSize()}\n")

def check_data_integrity(original_path, resampled_path):
    """检测重采样后数据完整性"""
    # 读取原始和重采样影像
    img_orig = sitk.ReadImage(original_path)
    img_resampled = sitk.ReadImage(resampled_path)
    
    # 转换为NumPy数组
    arr_orig = sitk.GetArrayFromImage(img_orig)
    arr_resampled = sitk.GetArrayFromImage(img_resampled)
    
    # ---------------------------
    # 1. 检查元数据一致性
    # ---------------------------
    print("[元数据检查]")
    print("原始影像 vs 重采样影像:")
    print(f"- 方向矩阵一致性: {img_orig.GetDirection() == img_resampled.GetDirection()}")
    print(f"- 原点一致性: {img_orig.GetOrigin() == img_resampled.GetOrigin()}")
    
    # ---------------------------
    # 2. 统计信息检查
    # ---------------------------
    print("\n[统计信息检查]")
    print(f"原始影像像素范围: [{np.min(arr_orig)}, {np.max(arr_orig)}]")
    print(f"重采样影像像素范围: [{np.min(arr_resampled)}, {np.max(arr_resampled)}]")
    
    # 检测是否存在异常截断（如PET值全为0）
    if np.max(arr_resampled) == 0:
        print("警告: 重采样后图像像素值全为0，可能存在数据丢失！")
        
    # ---------------------------
    # 3. 图像完整性检查（切片可视化）
    # ---------------------------
    print("\n[切片可视化检查]")
    # 随机选取中间切片
    slice_idx = arr_resampled.shape[0] // 2
    
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(arr_orig[slice_idx], cmap='gray')
    plt.title("Original Slice")
    
    plt.subplot(1, 2, 2)
    plt.imshow(arr_resampled[slice_idx], cmap='gray')
    plt.title("Resampled Slice")
    
    plt.show()
    
    # ---------------------------
    # 4. 模态对齐检查（仅限多模态数据）
    # ---------------------------
    # 如果需要检查MRI和PET对齐，需读取两种模态影像
    # 此处示例假设已有配准后的MRI和PET
    # 可通过检查空间参数或计算互信息验证对齐

def main():
    # 原始和重采样影像路径
    original_mri_path = rf"C:\Users\dongz\Desktop\adni_dataset\MRI\002_S_2010.nii"
    resampled_mri_path = rf"C:\Users\dongz\Desktop\adni_dataset\MRI-1\002_S_2010.nii"
    
    # 执行检查
    check_image_properties(original_mri_path)
    check_image_properties(resampled_mri_path)
    check_data_integrity(original_mri_path, resampled_mri_path)

if __name__ == "__main__":
    main()