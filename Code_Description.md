# ADNI Image Preprocessing and Analysis Code Overview
> A complete MRI-PET preprocessing, QC, and statistical workflow for **AD/MCI vs. NC** studies.
> The project maintains parallel MATLAB-SPM and pure Python/ITK pipelines, making it easy to switch between Windows-MATLAB and Linux-Docker environments.

---

## 1. Directory Overview

├─mat_tools/ # MATLAB-SPM batch-processing scripts

├─normalization/ # PET/MRI intensity normalization (Python)

├─py_tools/ # General-purpose Python image-processing scripts

├─skull_separation/ # PET skull stripping (Python single-case/batch processing)

└─utils/ # Templates, dictionaries, conversion tools, etc.


---

## 2. `mat_tools/` -- SPM Batch Scripts

| File | Purpose | Typical Input -> Output |
|------|---------|--------------------------|
| `batch_coregister_mri.m` | **MRI -> MNI registration** | Raw T1 -> rT1 |
| `batch_coregister_pet.m` | **PET -> MRI registration**, including normalization | PET -> wrPET |
| `batch_norm_MRI_only.m` | Run SPM **Normalization** on MRI only | T1 -> wrT1 |
| `coregister_job.m` | General registration helper called by `batch_coregister_*` | -- |
| `normalise_job.m` | Low-level wrapper for SPM Normalise | -- |
| `PET_batch_skull_separation.m` | Calls `imcalc`: `PET x (MRI > 0)` for batch PET skull stripping | wrPET + p0mask -> skullfree_wrPET |
| `Smooth.m` | Gaussian smoothing with a custom FWHM kernel | skullfree_* -> s6_skullfree_* |
| `PET_Intensity.m` | Compute and write PET global intensity | PET -> `.csv` |
| `Fun_Split_4DTo3D.m` / `Main_Fun_Split_4DTo3D.m` | Split 4D fMRI/NIfTI into 3D volumes | 4D -> multiple 3D files |
| `p0mask_all_to_mni.m` | Batch-transform CAT12 `p0*` masks to MNI space with custom voxel size and resolution | p0mask -> wp0mask |
| `Reorient.m` / `spm_auto_reorient.m` | Semi-automatically align the AC-PC line and correct the header | Raw -> r* |
| `Reslice_ROI.m` | Resample atlas/ROI files into subject space | ROI -> Reslice_ROI |
| `err_*.log`, `*.ps` | Batch-processing errors, SPM graphical output, etc. | -- |

---

## 3. `skull_separation/` -- Fast Skull Stripping with float32 Precision (Python)

| File | Description |
|------|-------------|
| `skull_separation-single.py` | Single-case script: `PET.nii` + `p0mask.nii` -> `PET_brain.nii` |
| `skull_separation.py` | **Batch version** with configurable input/output directories and multithreading. |
| `QC.py` | Computes voxel distributions before and after skull stripping, volume differences, and histograms. |

> Differences from `mat_tools/PET_batch_skull_separation.m`:
> - The **Python** version preserves `float32`, which is convenient for later NumPy/torch processing, but it uses more storage space.
> - It does not resample automatically. PET and the mask must already be in the same space; in other words, register PET and MRI first, then skull-strip PET.
> - Optional `binary_opening` / `largest_component` morphological cleanup is included in the code but disabled by default.


---

## 4. `normalization/` -- PET/MRI Intensity Normalization

| File | Brief Description |
|------|-------------------|
| `adaptive_normal.py` | **Robust linear normalization**: maps the 0.1%-99.9% percentiles to \[-1, 1] and automatically treats NaN / +/-Inf as background. |
| `check.py` | Prints the minimum/maximum values before and after normalization for each case and generates a QC table. |
| `size_check.py` | Quickly summarizes the dimensions and voxel sizes of all NIfTI files in a folder. |
| `nii_check_results.txt` | Summary output from the checking scripts above. |


---

## 5. `py_tools/` -- General-Purpose Python Toolbox

> Python scripts for NIfTI/DICOM operations, spatial calibration, resampling, data QC, and file naming.
> **Dependencies**: Python 3.9+, Nibabel, SimpleITK, NumPy, Pandas, scikit-image, etc. Dependencies are also noted at the top of each script.

---

### (1) Path and File Management

| Script | Function |
|--------|----------|
| **`datapath_modif.py`** | Uniformly rewrites the data root directory, for example when paths need to be updated after moving to a new server. Supports:<br>- Batch replacement using JSON/YAML configuration<br>- Recursive scanning of CSV/TSV files and updating path columns |
| **`search_4D.py`** | Searches multi-level directories for 4D NIfTI files (dimension >= 4), then outputs a list or copies them to a target folder. |
| **`rename-1.py`** | Batch renaming script used by other scripts when saving processed results. Example: `sub-IMG_001.nii -> IMG_001.nii` |
| **`rename-2.py`** | Batch renaming script used by other scripts when saving processed results. Example: `IMG_001-smooth.nii -> IMG-001.nii` |
| **`rename+1.py`** | Batch renaming script used by other scripts when saving processed results. Example: `IMG_001.nii -> normal_IMG-001.nii` |

---

### (2) Format Conversion

| Script | Purpose |
|--------|---------|
| **`dcm2nii_all.py`** | Batch-calls **dcm2niix** to convert DICOM to NIfTI and automatically save files by subject/timepoint directories. |
| **`nii2gz.py`** | Batch conversion from `.nii` to `.nii.gz` for single files while preserving the header. |
| **`niigz2nii.py`** | Batch conversion from `.nii.gz` to `.nii` for single files while preserving the header. |

---

### (3) Image Size / Voxel Checks

| Script | Function |
|--------|----------|
| **`get_size&voxel.py`** | Reads the **voxel spacing** and **matrix size (shape)** for each NIfTI file in a folder and summarizes them into a CSV file. |
| **`checking_dim.py`** | Quickly detects abnormal files with inconsistent dimensions; an allowed tolerance can be configured, such as +/-1 pixel. |
| **`check_resample_image.py`** | Verifies the header before and after resampling: spacing, origin, and direction. It prints differences and generates a report. |

---

### (4) Registration / Resampling / Preprocessing

| Script | Description |
|--------|-------------|
| **`register_pet2mri.py`** | **SimpleITK** mutual-information registration: rigidly aligns PET to MRI and outputs the transformation matrix plus the aligned image. |
| **`resample.py`** | Resamples according to a **target spacing** with selectable interpolation methods (linear / nearest neighbor / B-Spline). The image size and voxel settings can be specified, which can also be used to remove black background margins. |
| **`resize.py`** | Resamples according to a **target voxel size** such as 1 mm or 1.5 mm and automatically adjusts the image size. |
| **`N4_Bias_correction.py`** | ITK-based **N4 bias-field correction** to remove low-frequency MRI intensity inhomogeneity. |
| **`ac_pc.py`** | Estimates AC-PC points using Otsu thresholding and midline projection, then rewrites the affine so the brain is horizontally aligned. This is useful for quick reorientation without MATLAB. |

---

### (5) Quality Control (QC)

| Script | Description |
|--------|-------------|
| **`PET_Intensity.py`** | Computes the global mean SUV or total counts for PET and writes the result to `PET_DATA.csv`. |
| **`qc_pet_mri.py`** | Generates PET-MRI overlay PNG images and computes mutual information/SSIM to visually check registration quality. |
| **`QC_Check.py`** | Comprehensive QC:<br>1. Reads multiple metrics, including size, spacing, intensity range, and mask volume<br>2. Applies rule-based PASS/FAIL decisions<br>3. Outputs a colored HTML report |

---

## 6. `utils/` -- Templates, Dictionaries, Conversion Tools, etc.

| Category | Typical Files | Description |
|----------|---------------|-------------|
| Templates & Atlases | `mni_icbm152_...nii`, `aal3.nii`, `Reslice_aal3.nii` | MNI standard brain and AAL3 templates at different resolutions |
| Dictionaries | `.csv` | Dictionary files describing brain templates and brain atlases |
| Conversion tools | `dcm2niix.exe` | DICOM-to-NIfTI conversion tool |


---

## 7. Notes
---

**Virtual environment**: It is recommended to create a separate Conda environment for the Python tools with `conda env create -f env_mri.yml` to avoid conflicts with system packages.

**Recommended Workflow**

1. **DICOM -> NIfTI** (`dcm2niix.exe` / `dcm2nii_all.py`)
2. **Initial reorientation** (`spm_auto_reorient.m` -> `Reorient.m`)
3. **MRI -> MNI / PET -> MRI, output wr*** (`batch_coregister_*`, `batch_norm_MRI_only.m`)
4. **CAT12 segmentation** to generate `p0*` (brain mask) and `y*` (deformation field to MNI space)
5. **MRI & PET skull stripping**, using either:
   - SPM: `PET_batch_skull_separation.m`
   - Python: `skull_separation.py`
6. **Smoothing**: PET with `PET_Smooth.m` (6 mm); choose 2 mm/4 mm for MRI as needed.
7. **Intensity normalization & resizing**: `adaptive_normal.py` -> `resize.py`
8. **Quality control**: `QC.py`, `QC_Check.py`, `qc_pet_mri.py`

---

## 8. FAQ

- **Can MATLAB and Python results be mixed?**
  Yes, as long as spatial alignment and data types are consistent. The Python stage can read either `.nii` or `.nii.gz` files.

- **Why keep two sets of scripts?**
  - SPM is more robust for **spatial transformations**, and its batch scripts are convenient for visualization.
  - Python is more flexible for **morphological cleanup / GPU inference**, and servers do not require a MATLAB license.

- **How should I determine the script execution order?**
  See the "Recommended Workflow" section. Steps can also be added or removed according to the experimental design.

---
