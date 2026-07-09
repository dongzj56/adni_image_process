import nibabel as nib
import numpy as np

def check_last_slices_are_background(nifti_path, background_value=0):
    """
    Check whether the last slice along each of the three dimensions is entirely background.

    Args:
    - nifti_path: Input NIfTI file path, assumed to have shape (113, 137, 113).
    - background_value: Background voxel value, usually 0.

    Returns:
    A dictionary containing these Boolean values:
      - 'x_slice_all_bg': Whether the slice at X-axis index 112 is all background.
      - 'y_slice_all_bg': Whether the slice at Y-axis index 136 is all background.
      - 'z_slice_all_bg': Whether the slice at Z-axis index 112 is all background.
    """
    img = nib.load(nifti_path)
    data = img.get_fdata()

    # Confirm the original shape is (113, 137, 113).
    if data.shape != (113, 137, 113):
        raise ValueError(f"Image shape is {data.shape}, not the expected (113, 137, 113).")

    # Last slice along the X direction: index 112.
    x_idx = data.shape[0] - 1  # 112
    x_slice = data[x_idx, :, :]

    # Last slice along the Y direction: index 136.
    y_idx = data.shape[1] - 1  # 136
    y_slice = data[:, y_idx, :]

    # Last slice along the Z direction: index 112.
    z_idx = data.shape[2] - 1  # 112
    z_slice = data[:, :, z_idx]

    results = {
        'x_slice_all_bg': np.all(x_slice == background_value),
        'y_slice_all_bg': np.all(y_slice == background_value),
        'z_slice_all_bg': np.all(z_slice == background_value),
    }
    return results


if __name__ == "__main__":
    # Example: replace the path below with your NIfTI file path.
    nifti_file = rf"GM\002_S_2043.nii"
    check_result = check_last_slices_are_background(nifti_file)

    print("Check results:")
    print(f"Is the slice at X-axis index 112 all background? {'yes' if check_result['x_slice_all_bg'] else 'no'}")
    print(f"Is the slice at Y-axis index 136 all background? {'yes' if check_result['y_slice_all_bg'] else 'no'}")
    print(f"Is the slice at Z-axis index 112 all background? {'yes' if check_result['z_slice_all_bg'] else 'no'}")
