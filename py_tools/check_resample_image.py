'''Data quality checks before and after resampling.'''
import os
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

def check_image_properties(image_path):
    """Check image metadata."""
    image = sitk.ReadImage(image_path)
    print(f"File: {os.path.basename(image_path)}")
    print(f"Origin: {image.GetOrigin()}")
    print(f"Direction: {image.GetDirection()}")
    print(f"Spacing: {image.GetSpacing()}")
    print(f"Size: {image.GetSize()}\n")

def check_data_integrity(original_path, resampled_path):
    """Check data integrity after resampling."""
    # Read the original and resampled images.
    img_orig = sitk.ReadImage(original_path)
    img_resampled = sitk.ReadImage(resampled_path)
    
    # Convert to NumPy arrays.
    arr_orig = sitk.GetArrayFromImage(img_orig)
    arr_resampled = sitk.GetArrayFromImage(img_resampled)
    
    # ---------------------------
    # 1. Check metadata consistency.
    # ---------------------------
    print("[Metadata Check]")
    print("Original image vs. resampled image:")
    print(f"- Direction matrix consistency: {img_orig.GetDirection() == img_resampled.GetDirection()}")
    print(f"- Origin consistency: {img_orig.GetOrigin() == img_resampled.GetOrigin()}")
    
    # ---------------------------
    # 2. Statistical checks.
    # ---------------------------
    print("\n[Statistical Check]")
    print(f"Original image pixel range: [{np.min(arr_orig)}, {np.max(arr_orig)}]")
    print(f"Resampled image pixel range: [{np.min(arr_resampled)}, {np.max(arr_resampled)}]")
    
    # Detect abnormal truncation, such as all-zero PET values.
    if np.max(arr_resampled) == 0:
        print("Warning: all resampled image pixel values are 0; data may have been lost.")
        
    # ---------------------------
    # 3. Image-integrity check with slice visualization.
    # ---------------------------
    print("\n[Slice Visualization Check]")
    # Select the middle slice.
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
    # 4. Modality-alignment check for multimodal data only.
    # ---------------------------
    # To check MRI-PET alignment, read both modalities.
    # This example assumes registered MRI and PET are already available.
    # Alignment can be verified by checking spatial parameters or computing mutual information.

def main():
    # Original and resampled image paths.
    original_mri_path = rf"C:\Users\dongz\Desktop\adni_dataset\MRI\002_S_2010.nii"
    resampled_mri_path = rf"C:\Users\dongz\Desktop\adni_dataset\MRI-1\002_S_2010.nii"
    
    # Run checks.
    check_image_properties(original_mri_path)
    check_image_properties(resampled_mri_path)
    check_data_integrity(original_mri_path, resampled_mri_path)

if __name__ == "__main__":
    main()
