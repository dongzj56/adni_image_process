import os
import numpy as np
import nibabel as nib
import scipy.ndimage as ndi  # Required for morphological operations.

# ---------- 0. Paths ----------
input_image_dir = rf'F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\01PET_registered\MNI_1mm'
input_mask_dir  = rf'F:\ADNI_dataset_902_samples\05-MRI_skull_stripping\p0original\01registered_to_MNI\1mm'
output_dir      = rf'F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\02PET_skull_stripped\MNI_1mm'
os.makedirs(output_dir, exist_ok=True)

# ---------- 1. Iterate ----------
for image_fname in os.listdir(input_image_dir):
    if not image_fname.endswith('.nii'):
        continue

    # 1.1 Read the original T1 / wm image.
    img_path = os.path.join(input_image_dir, image_fname)
    img_nii  = nib.load(img_path)
    img_data = img_nii.get_fdata()            # float64 by default

    # 1.2 Build the corresponding mask filename.
    mask_fname = 'p0' + image_fname.replace('original_image', 'mask_series')
    mask_path  = os.path.join(input_mask_dir, mask_fname)
    if not os.path.exists(mask_path):
        print(f'[WARN] Mask not found for: {image_fname}')
        continue

    # ---------- 2. Process the mask ----------
    mask_data = nib.load(mask_path).get_fdata()
    mask_bool = mask_data > 0                 # Treat p0 labels 1-3 as brain.

    # Optional: opening to remove spikes, closing to fill holes, and keep only the largest connected component.
    # mask_bool = ndi.binary_opening(mask_bool, iterations=1)
    # mask_bool = ndi.binary_closing(mask_bool, iterations=1)
    # labeled, _ = ndi.label(mask_bool)
    # largest = np.argmax(np.bincount(labeled.ravel())[1:]) + 1
    # mask_bool = labeled == largest

    # ---------- 3. Apply the mask to the original image ----------
    out_data = img_data * mask_bool

    # ---------- 4. Force output to float32 ----------
    out_data = out_data.astype(np.float32)
    out_nii  = nib.Nifti1Image(out_data, affine=img_nii.affine, header=img_nii.header)
    out_nii.header.set_data_dtype(np.float32)  # Keep header dtype in sync.

    # ---------- 5. Save ----------
    out_fname = image_fname.replace('.nii', '_brain.nii')
    nib.save(out_nii, os.path.join(output_dir, out_fname))
    print(f'[OK] Saved: {out_fname}')

print('All processing complete.')
