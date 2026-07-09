from nibabel.viewers import OrthoSlicer3D
import nibabel as nib
import numpy as np

# Load the original image sequence.
orig_nii = nib.load('test_data/002_S_4213.nii')
original_image = nib.load('test_data/002_S_4213.nii').get_fdata()

# Load the mask sequence.
mask_sequence = nib.load('test_data/p0002_S_4213.nii').get_fdata()

# Combine the mask sequence with the original image sequence.
output_sequence = original_image * mask_sequence

# Save the output image sequence.
output_image = nib.Nifti1Image(output_sequence, affine=orig_nii.affine)
nib.save(output_image, 'path_to_output_image.nii.gz')
