'''Resize images according to voxel size.'''
import nibabel as nib
import numpy as np
from scipy.ndimage import zoom
import os

def resample_nifti(input_path, output_path, new_voxel_size):
    """
    Read a NIfTI image, resample it according to a new voxel size, and save it.

    Args:
    - input_path: Original NIfTI file path.
    - output_path: Output path for the resampled NIfTI file.
    - new_voxel_size: New voxel size as a tuple (vx, vy, vz), in millimeters.
    """
    # 1. Read the original image.
    img = nib.load(input_path)
    data = img.get_fdata()
    affine = img.affine.copy()
    header = img.header.copy()

    # 2. Get the original size and voxel size.
    orig_shape = data.shape
    orig_voxel_size = header.get_zooms()[:3]
    print(f"Processing file: {os.path.basename(input_path)}")
    print("Original size:", orig_shape)
    print("Original voxel size:", orig_voxel_size)

    # 3. Compute the scale factor for each direction.
    scale_factors = tuple(orig_voxel_size[i] / new_voxel_size[i] for i in range(3))

    # 4. Run resampling with bilinear interpolation.
    resampled_data = zoom(data, scale_factors, order=1)

    # 5. Compute the new size.
    new_shape = resampled_data.shape

    # 6. Build a new affine by modifying only the diagonal voxel-size terms.
    new_affine = affine.copy()
    for i in range(3):
        new_affine[i, i] = new_voxel_size[i]

    # 7. Update voxel size in the header.
    new_header = header.copy()
    new_header.set_zooms(new_voxel_size)

    # 8. Save the new NIfTI image.
    new_img = nib.Nifti1Image(resampled_data, new_affine, header=new_header)
    nib.save(new_img, output_path)

    # 9. Print results.
    print("Resampled size:", new_shape)
    print("New voxel size:", new_voxel_size)
    print(f"Saved to: {output_path}\n")


def process_directory(input_dir, output_dir, new_voxel_size):
    """
    Process all NIfTI files in the specified directory.
    
    Args:
    - input_dir: Input directory path.
    - output_dir: Output directory path.
    - new_voxel_size: New voxel size.
    """
    # Ensure the output directory exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Get all NIfTI files.
    nifti_files = [f for f in os.listdir(input_dir) if f.endswith(('.nii', '.nii.gz'))]
    
    if not nifti_files:
        print(f"No NIfTI files (.nii or .nii.gz) found in {input_dir}")
        return
    
    print(f"Found {len(nifti_files)} NIfTI files")
    
    # Process each file.
    for filename in nifti_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            resample_nifti(input_path, output_path, new_voxel_size)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print("All files processed.")


if __name__ == "__main__":
    # Get input from the user.
    input_dir = input("Enter the directory path containing NIfTI files: ")
    output_dir = input("Enter the output directory for resampled files: ")
    
    # Set target voxel size.
    new_voxel_size = (1.5, 1.5, 1.5)  # Default target voxel size.
    
    # Process all files in the directory.
    process_directory(input_dir, output_dir, new_voxel_size)
