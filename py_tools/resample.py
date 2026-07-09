'''Resample images to a fixed size and voxel spacing.'''
import os
import SimpleITK as sitk

def resample_image(input_path, output_dir, target_size=(96, 112, 96), target_spacing=(2, 2, 2)):
    """
    Resample a medical image to the specified size and voxel spacing.
    :param input_path: Input image path, supporting .nii/.nii.gz.
    :param output_dir: Output directory.
    :param target_size: Target size (depth, height, width).
    :param target_spacing: Target voxel spacing (z, y, x), in millimeters.
    """
    # Read the image.
    image = sitk.ReadImage(input_path)
    
    # Configure resampling parameters.
    resampler = sitk.ResampleImageFilter()
    resampler.SetSize(target_size)
    resampler.SetOutputSpacing(target_spacing)
    resampler.SetOutputDirection(image.GetDirection())
    resampler.SetOutputOrigin(image.GetOrigin())
    resampler.SetTransform(sitk.Transform())
    resampler.SetInterpolator(sitk.sitkLinear)  # Use linear interpolation.
    
    # Run resampling.
    resampled_image = resampler.Execute(image)
    
    # Save the result.
    filename = os.path.basename(input_path)
    output_path = os.path.join(output_dir, filename)
    sitk.WriteImage(resampled_image, output_path)
    print(f"Saved resampled image to: {output_path}")

# Example.
if __name__ == "__main__":
    # Input and output paths. Replace these with actual paths.
    mri_dir = rf"C:\Users\dongz\Desktop\resize"
    # pet_dir = rf"C:\Users\dongz\Desktop\adni_dataset\PET"
    output_mri_dir = rf"C:\Users\dongz\Desktop\resize\out"  # MRI output directory.
    # output_pet_dir = rf"C:\Users\dongz\Desktop\adni_dataset\PET"  # PET output directory.
    
    # Create output directories.
    os.makedirs(output_mri_dir, exist_ok=True)
    # os.makedirs(output_pet_dir, exist_ok=True)
    
    # Process MRI images and save them to output_mri_dir.
    for filename in os.listdir(mri_dir):
        if filename.endswith(('.nii', '.nii.gz')):
            input_path = os.path.join(mri_dir, filename)
            resample_image(input_path, output_mri_dir)  # Specify the MRI output directory.
    
    # # Process PET images and save them to output_pet_dir.
    # for filename in os.listdir(pet_dir):
    #     if filename.endswith(('.nii', '.nii.gz')):
    #         input_path = os.path.join(pet_dir, filename)
    #         resample_image(input_path, output_pet_dir)  # Specify the PET output directory.
