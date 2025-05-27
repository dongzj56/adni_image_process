'''配准mri和pet'''
import os
import SimpleITK as sitk
from tqdm import tqdm

def register_pet_to_mri(pet_image_path, mri_image_path, output_path):
    """
    将PET图像配准到MRI图像的空间并保存结果。

    :param pet_image_path: 输入的PET图像路径
    :param mri_image_path: 参考的MRI图像路径
    :param output_path: 输出的图像保存路径
    """
    # 读取PET和MRI图像
    pet_image = sitk.ReadImage(pet_image_path)
    mri_image = sitk.ReadImage(mri_image_path)

    # 使用仿射变换进行配准
    # 创建配准方法
    initial_transform = sitk.CenteredTransformInitializer(mri_image, pet_image, sitk.Euler3DTransform())
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMeanSquares()
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100)
    registration_method.SetInitialTransform(initial_transform)  # 使用SetInitialTransform代替SetTransform
    registration_method.SetShrinkFactorsPerLevel([4, 2, 1])
    registration_method.SetSmoothingSigmasPerLevel([2, 1, 0])
    
    # 执行配准
    final_transform = registration_method.Execute(mri_image, pet_image)

    # 应用最终的变换到PET图像
    resampled_pet_image = sitk.Resample(pet_image, mri_image, final_transform, sitk.sitkLinear, 0.0, pet_image.GetPixelID())

    # 保存配准后的PET图像
    sitk.WriteImage(resampled_pet_image, output_path)

def batch_register_pet_to_mri(pet_dir, mri_dir, output_dir_pet, output_dir_mri):
    """
    批量将PET图像配准到MRI图像空间，并保存输出。
    
    :param pet_dir: 存放PET图像的目录
    :param mri_dir: 存放MRI图像的目录
    :param output_dir_pet: 配准后PET图像保存目录
    :param output_dir_mri: 配准后MRI图像保存目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir_pet, exist_ok=True)
    os.makedirs(output_dir_mri, exist_ok=True)

    # 获取所有PET图像文件
    pet_files = [f for f in os.listdir(pet_dir) if f.endswith('.nii') or f.endswith('.nii.gz')]
    
    # 遍历PET图像
    for pet_file in tqdm(pet_files, desc="Processing PET images"):
        pet_image_path = os.path.join(pet_dir, pet_file)
        mri_image_path = os.path.join(mri_dir, pet_file)  # 假设PET和MRI图像有相同的文件名
        
        if os.path.exists(mri_image_path):
            # 配准并保存结果
            output_pet_path = os.path.join(output_dir_pet, pet_file)
            register_pet_to_mri(pet_image_path, mri_image_path, output_pet_path)

if __name__ == "__main__":
    # 示例路径
    pet_dir = rf'data\MRI'
    mri_dir = rf'data\PET'
    output_dir_pet = rf'data\MRI-1'
    output_dir_mri = rf'data\PET-1'

    # 批量处理PET到MRI的配准
    batch_register_pet_to_mri(pet_dir, mri_dir, output_dir_pet, output_dir_mri)
