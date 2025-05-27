'''重采样，设置固定大小和体素'''
import os
import SimpleITK as sitk

def resample_image(input_path, output_dir, target_size=(96, 112, 96), target_spacing=(2, 2, 2)):
    """
    重采样医学影像到指定尺寸和体素大小
    :param input_path: 输入影像路径（支持.nii/.nii.gz）
    :param output_dir: 输出目录
    :param target_size: 目标尺寸 (depth, height, width)
    :param target_spacing: 目标体素大小 (z, y, x) 单位：毫米
    """
    # 读取影像
    image = sitk.ReadImage(input_path)
    
    # 计算重采样参数
    resampler = sitk.ResampleImageFilter()
    resampler.SetSize(target_size)
    resampler.SetOutputSpacing(target_spacing)
    resampler.SetOutputDirection(image.GetDirection())
    resampler.SetOutputOrigin(image.GetOrigin())
    resampler.SetTransform(sitk.Transform())
    resampler.SetInterpolator(sitk.sitkLinear)  # 使用线性插值
    
    # 执行重采样
    resampled_image = resampler.Execute(image)
    
    # 保存结果
    filename = os.path.basename(input_path)
    output_path = os.path.join(output_dir, filename)
    sitk.WriteImage(resampled_image, output_path)
    print(f"Saved resampled image to: {output_path}")

# 使用示例
if __name__ == "__main__":
    # 输入路径和输出路径（替换为实际路径）
    mri_dir = rf"C:\Users\dongz\Desktop\resize"
    # pet_dir = rf"C:\Users\dongz\Desktop\adni_dataset\PET"
    output_mri_dir = rf"C:\Users\dongz\Desktop\resize\out"  # MRI输出目录
    # output_pet_dir = rf"C:\Users\dongz\Desktop\adni_dataset\PET"  # PET输出目录
    
    # 创建输出目录
    os.makedirs(output_mri_dir, exist_ok=True)
    # os.makedirs(output_pet_dir, exist_ok=True)
    
    # 处理MRI影像，保存到output_mri_dir
    for filename in os.listdir(mri_dir):
        if filename.endswith(('.nii', '.nii.gz')):
            input_path = os.path.join(mri_dir, filename)
            resample_image(input_path, output_mri_dir)  # 指定MRI输出目录
    
    # # 处理PET影像，保存到output_pet_dir
    # for filename in os.listdir(pet_dir):
    #     if filename.endswith(('.nii', '.nii.gz')):
    #         input_path = os.path.join(pet_dir, filename)
    #         resample_image(input_path, output_pet_dir)  # 指定PET输出目录