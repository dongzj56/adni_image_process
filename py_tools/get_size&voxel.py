'''Get image size and voxel spacing for files in a directory.'''
import os
import nibabel as nib
import pydicom

def get_image_size_and_voxel(image_path):
    """
    Get image size and voxel spacing. Supports NIfTI and DICOM files.
    """
    if image_path.endswith('.nii') or image_path.endswith('.nii.gz'):
        # Read the NIfTI image.
        img = nib.load(image_path)
        size = img.shape  # Image size (depth, height, width).
        voxel_size = img.header.get_zooms()  # Voxel spacing.
        return size, voxel_size
    
    elif image_path.endswith('.dcm'):
        # Read the DICOM image.
        ds = pydicom.dcmread(image_path)
        size = (ds.Rows, ds.Columns)  # Return DICOM image size (height, width).
        
        # Get voxel spacing for 3D DICOM images.
        if 'SpacingBetweenSlices' in ds and 'PixelSpacing' in ds:
            voxel_size = (ds.PixelSpacing[0], ds.PixelSpacing[1], ds.SpacingBetweenSlices)
        else:
            voxel_size = None
        
        return size, voxel_size
    
    else:
        return None, None

def print_image_sizes_and_voxels(directory):
    """
    Iterate through a directory and print image size and voxel spacing for all image files.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.nii') or file.endswith('.nii.gz') or file.endswith('.dcm'):
                size, voxel_size = get_image_size_and_voxel(file_path)
                if size:
                    voxel_info = f"Voxel Size: {voxel_size}" if voxel_size else "Voxel Size: N/A"
                    print(f"File: {file_path} | Size: {size} | {voxel_info}")
                else:
                    print(f"File: {file_path} | Unsupported file format")

# Example directory path.
directory = rf'C:\Users\dongz\Desktop\test'

# Print image size and voxel spacing for all image files.
print_image_sizes_and_voxels(directory)
