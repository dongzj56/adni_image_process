import os, glob, sys, locale
from pathlib import Path
import numpy as np
import SimpleITK as sitk

# ---- Force UTF-8 on Windows to avoid encoding issues. ----
if sys.platform.startswith("win"):
    os.environ.setdefault("PYTHONUTF8", "1")
    try:
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    except locale.Error:
        pass


def adaptive_normal(image_path: str, outpath: str, eps: float = 1e-6) -> str:
    """
    Robust intensity normalisation to [-1, 1] using 0.1%–99.9% quantiles.
    NaN / +/-Inf values are treated as background (-1) to avoid corrupting percentile statistics.
    """
    # Read the image and convert it to float32.
    img = sitk.ReadImage(image_path)
    arr = sitk.GetArrayFromImage(img).astype(np.float32)

    # Map NaN and Inf to -1 as background.
    arr[~np.isfinite(arr)] = -1.0

    # Foreground voxels (>0).
    fg = arr[arr > 0]
    if fg.size == 0:                               # Entire image is background.
        print(f"[WARN] All-zero image: {image_path}")
        sitk.WriteImage(img, outpath)
        return os.path.abspath(outpath)

    # 0.1%-99.9% percentiles.
    lo, hi = np.percentile(fg, [0.1, 99.9])
    std = max((hi - lo) / 2.0, eps)               # Add epsilon to avoid division by zero.
    mean = (hi + lo) / 2.0

    # Normalize and clip to [-1, 1].
    arr = np.clip((arr - mean) / std, -1.0, 1.0)

    # Write back to NIfTI while preserving spatial information.
    out_img = sitk.GetImageFromArray(arr)
    out_img.CopyInformation(img)
    sitk.WriteImage(out_img, outpath)
    return os.path.abspath(outpath)


def adaptive_normal_dir(in_dir: str, out_dir: str):
    """
    Batch-process all .nii / .nii.gz files in a directory.
    """
    os.makedirs(out_dir, exist_ok=True)
    nii_list = glob.glob(os.path.join(in_dir, "*.nii*"))

    for nii_path in nii_list:
        fname = Path(nii_path).name
        out_path = os.path.join(out_dir, fname)
        adaptive_normal(nii_path, out_path)
        print(f"Processed: {fname}  →  {out_path}")


# --------------------- Example ---------------------
if __name__ == "__main__":
    src = rf"F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\03PET_smoothing4mm\MNI_1mm"
    dst = rf"F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\04PET_normalized\MNI_1mm"
    adaptive_normal_dir(src, dst)
