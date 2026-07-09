'''Register MRI and PET images.'''
import os
import SimpleITK as sitk
from tqdm import tqdm

def register_pet_to_mri(pet_image_path, mri_image_path, output_path):
    """
    Register a PET image to MRI image space and save the result.

    :param pet_image_path: Input PET image path.
    :param mri_image_path: Reference MRI image path.
    :param output_path: Output image path.
    """
    # Read PET and MRI images.
    pet_image = sitk.ReadImage(pet_image_path)
    mri_image = sitk.ReadImage(mri_image_path)

    # Register using an affine transform.
    # Create the registration method.
    initial_transform = sitk.CenteredTransformInitializer(mri_image, pet_image, sitk.Euler3DTransform())
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMeanSquares()
    registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100)
    registration_method.SetInitialTransform(initial_transform)  # Use SetInitialTransform instead of SetTransform.
    registration_method.SetShrinkFactorsPerLevel([4, 2, 1])
    registration_method.SetSmoothingSigmasPerLevel([2, 1, 0])
    
    # Run registration.
    final_transform = registration_method.Execute(mri_image, pet_image)

    # Apply the final transform to the PET image.
    resampled_pet_image = sitk.Resample(pet_image, mri_image, final_transform, sitk.sitkLinear, 0.0, pet_image.GetPixelID())

    # Save the registered PET image.
    sitk.WriteImage(resampled_pet_image, output_path)

def batch_register_pet_to_mri(pet_dir, mri_dir, output_dir_pet, output_dir_mri):
    """
    Batch-register PET images to MRI image space and save the outputs.
    
    :param pet_dir: Directory containing PET images.
    :param mri_dir: Directory containing MRI images.
    :param output_dir_pet: Output directory for registered PET images.
    :param output_dir_mri: Output directory for registered MRI images.
    """
    # Ensure output directories exist.
    os.makedirs(output_dir_pet, exist_ok=True)
    os.makedirs(output_dir_mri, exist_ok=True)

    # Get all PET image files.
    pet_files = [f for f in os.listdir(pet_dir) if f.endswith('.nii') or f.endswith('.nii.gz')]
    
    # Iterate over PET images.
    for pet_file in tqdm(pet_files, desc="Processing PET images"):
        pet_image_path = os.path.join(pet_dir, pet_file)
        mri_image_path = os.path.join(mri_dir, pet_file)  # Assume PET and MRI images share the same filename.
        
        if os.path.exists(mri_image_path):
            # Register and save the result.
            output_pet_path = os.path.join(output_dir_pet, pet_file)
            register_pet_to_mri(pet_image_path, mri_image_path, output_pet_path)

if __name__ == "__main__":
    # Example paths.
    pet_dir = rf'data\MRI'
    mri_dir = rf'data\PET'
    output_dir_pet = rf'data\MRI-1'
    output_dir_mri = rf'data\PET-1'

    # Batch-process PET-to-MRI registration.
    batch_register_pet_to_mri(pet_dir, mri_dir, output_dir_pet, output_dir_mri)
