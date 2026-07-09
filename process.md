# ADNI Image Data Preprocessing Guide

# MRI Processing Workflow

## Step 1: Data Format Conversion
### 1. Convert `.dcm` files to `.nii` format
Run `dcm2nii_all.py` to batch-process DICOM files in the ADNI image download directory and save them as NIfTI files. Running this script will not delete the original DICOM files.

Change `root_dir = r'ADNI_Image_MRI\ADNI'` to the image download path before running the script.
Change `dcm2niix_path = r'tools\dcm2niix.exe'` to your own local path.

`dcm2niix.exe` can be downloaded from `https://github.com/rordenlab/dcm2niix/releases`, or found under the resources directory of MRIcron.
### 2. Modify the dataset storage format for later use
Run `datapath_modif.py` to reorganize the dataset storage structure, making later preprocessing and model training easier. This script is optional and can be used as needed.

Change `root_dir = r"ADNI_Image_MRI\ADNI"` in the code to the image download path.

###### Dataset Structure

```plaintext
.
├── MRI/                    # MRI data
│   ├── 002_S_2010.nii
│   ├── 002_S_2043.nii
│   └── ...
├── PET/                    # PET data
│   ├── 002_S_2010.nii
│   ├── 002_S_2043.nii
│   └── ...
|——table/                   # Non-imaging data
|   |——cognitive_test
|   |——Biomarkers_test
|   └──...
└── train_label.csv         # Labels
```

## Step 2: AC-PC Correction

Set the image coordinate origin to the AC-PC line to facilitate later registration.
SPM, a widely used neuroimaging toolbox in MATLAB, provides an integrated AC-PC correction function after configuration.

### 1. Manual Correction
Manual correction can be performed with SPM or ITK-SNAP.

### 2. Batch Correction
Refer to the batch correction code `spm_auto_reorient.m` from `https://github.com/CyclotronResearchCentre/spm_auto_reorient`; configure the `cfg` file and run it.

Running `spm_auto_reorient.m` directly may produce errors. The original batch-processing code was modified into `Reorient.m`, which is recommended.

Code settings: `i_type = 't1'` performs AC-PC correction for T1-weighted MRI images.
`i_type = 'pet'` performs correction for PET images. For other image types, modify the corresponding parameters.

1. MRI and PET images need to be processed separately. Corrected files overwrite the original files, so back up the originals first.

2. The generated `temp.nii` file should be deleted automatically. If it is not deleted, manually remove it before running the script again.

3. If the AC location is too far from the expected position, template matching may fail with the error: `There is not enough overlap in the images to obtain a solution.` For NIfTI files that produce this error, first use MRIcron or SPM to manually move them to an approximate position, then run batch processing again.

In `Reorient.m`, `center_origin=true` is enabled. This first sets the AC point of the image to the center position, making template matching successful in most cases.

A Python implementation for AC-PC correction is also provided as `ac_pc.py`, but its correction performance has not yet been comparatively validated.

### MRI Image Comparison Before and After AC-PC Correction

The left image is the original image, and the right image is after AC-PC correction.

###### 941_S_4377
![image](img\ADNI_941_S_4377_original.png "Magic Gardens")![image](img\ADNI_941_S_4377_acpc.png "Magic Gardens")

###### 941_S_4764
![image](img\ADNI_941_S_4764_original.png "Magic Gardens")![image](img\ADNI_941_S_4764_acpc.png "Magic Gardens")

## Step 3: Bias Correction and Spatial Registration

During MRI acquisition, signal intensity from the same tissue can vary across locations because of magnetic-field inhomogeneity or differences in RF coil sensitivity. For example, brain gray matter may appear brighter near the image center and darker near the edges. This intensity inhomogeneity can interfere with later analyses, such as tissue segmentation and quantitative measurement, so N3 or N4 correction is needed.

### 1. N4 Correction
Run `N4_Bias_correction.py` to perform N4 correction.

This step can be skipped because later MRI skull stripping can optionally perform bias correction and registration using the AAL3 template.

If the images downloaded from ADNI are already preprocessed, they usually have undergone N3 bias correction. You can inspect the images and apply N4 correction to selected cases if needed.

### 2. Registration
Batch registration code is provided as `batch_coregister_mri.m`. Because registration can also be performed during skull stripping, this step can also be skipped.

## Step 4: MRI Skull Stripping

Use the MATLAB-integrated CAT12 toolbox for skull stripping and segment brain tissue into gray matter, white matter, and cerebrospinal fluid.

###### Note

Before MRI skull stripping, you can use SPM12 to choose a template for registration. However, this has little impact on the preprocessing results because CAT12 automatically performs spatial registration during skull stripping, transforming images from native space to MNI standard space.

### 1. Skull Stripping with CAT12
Select `segment` in CAT12 and modify the following parameters.

###### Parameter 1
Set `own atlas maps` to the `aal3.nii` template under `spm12\toolbox\cat12\templates_MNI152NLin2009cAsym`.
###### Parameter 2
`Surface and thickness estimation` refers to cortical surface data. Select `No` if it is not needed.
###### Parameter 3
For `Deformation Fields`, select `inverse+forward`, or select only `forward`, which means registering the individual image to the standard template. If brain-region results are needed, select `reverse` to map template brain-region labels back to the individual image.
###### Parameter 4
Set `PVE label image in native space` to `Yes`.
###### Parameter 5
Set `Normalized` to `Yes` to perform bias-field correction.

Files beginning with `y` generated during skull stripping are mapping parameters from native space to standard space. Do not delete them, because they are used later to register PET images.

`skull_separation.py` can use the mask generated from skull stripping to segment the original image and obtain a brain image with the skull removed. Registration can be performed again after segmentation if needed.

# PET Processing Workflow

Not every MRI image has a corresponding PET modality. The data must be filtered first. In the ADNI1-3 datasets, approximately 1,251 subjects have both MRI and PET modality data.

## Step 1: Format Conversion
This is the same as the MRI image-processing step.

## Step 2: Convert 4D PET to 3D
PET images are 4D and contain multiple temporal slices. They need to be converted to 3D before processing. Batch-processing code is provided as `Main_Fun_Split_4DTo3D.m`; only the path and number of slices need to be modified to perform 4D-to-3D conversion.

All 4D PET data have at least two frames. In addition, 197 4D PET images have six frames. To use as much data as possible, the first extracted frame is used as the 3D image converted from 4D.

## Step 3: AC-PC Correction
This is the same as the MRI image-processing step. The corresponding parameter in the code must be changed to `i_type = 'pet'`; otherwise, correction will be performed with the MRI template.

## Step 4: Registration to MRI

Batch-processing script: `batch_coregister_pet.m`. Modify the path parameters. The reference image is the skull-stripped MRI.

1. Set `outputPrefix = 'wr'`, which means both normalization/bias-field correction and registration are performed. If correction is not needed, set `outputPrefix = 'r'`.

2. Set `interp = 1` to use linear interpolation during transformation, which is computationally efficient. Because PET has relatively low resolution, linear interpolation is sufficient. You can also set `interp` to 4-7 for higher-order interpolation, which produces smoother results.

During MRI skull stripping, files beginning with `y` are generated as transformation parameters from native space to MNI standard space. These parameters can be directly used to normalize PET images. The registration script calls `normalise_job.m` to implement this function.

Two parameters in `normalise_job.m` need to be modified when calling it:

1. Bounding box parameters: the number of voxels in the output PET image, namely the image dimensions. I set `bb = [-84 -103 -79;84 102 90]` and `vox = [1.5 1.5 1.5]` to match the processed MRI size.
2. Voxel-size parameter: the voxel size. Most papers use `[1 1 1]` or `[2 2 2]`. If the AAL template itself has a voxel size of 1, set `vox = [1 1 1]`.


###### Comparison Before and After Registration for 002_S_2010
![image](img\002_S_2010.png "Magic Gardens")![image](img\wr002_S_2010.png "Magic Gardens")

## Step 5: Calculate Mean PET Intensity in ROIs
If three-dimensional convolution is used to extract features directly, this step can be ignored. You can compare the performance difference between the two approaches.

### 1. Principle
The voxel size of the PET image is 1 x 1 x 1 mm3, and each voxel value represents radioactive uptake intensity, such as an SUV value.

To calculate the value of a specific brain region, find the corresponding region index in the AAL3 template, then calculate the mean pixel value at the positions corresponding to that index. This value can be used as an uptake-intensity feature, namely a metabolic feature.

### 2. Adjustment Before Calculation

Open the registered and normalized PET image, whose filename begins with `wr`, and load the AAL3 template at the same time. The two images can be seen to overlap completely, as shown in the two images below:

![image](img\aal+2010.png "Magic Gardens") ![image](img\aal+2043.png "Magic Gardens")


However, during calculation, the registered PET image and the AAL3 template were found to have different dimensions and coordinate origins, so the values at the corresponding AAL brain-region positions could not be calculated directly. Adjustment is required.

In the figure below, the left image is the registered PET image. The MNI standard-space coordinate origin corresponds to position `(101, 131, 91)`, and the image dimensions are `201 x 221 x 196`. The AAL3 coordinate origin is `(81, 117, 73)`, and the image dimensions are `161 x 197 x 161`.

![image](img\wr002_S_2010_mat.png "Magic Gardens") ![image](img\aal3.png "Magic Gardens")

Images with different sizes and different coordinate origins can still correspond to each other because registration uses an affine transformation matrix that maps voxel coordinates to MNI coordinates. Therefore, images with different dimensions can still be matched.

Formula: `MNI_cor = affine * [x, y, z, 1]T`, where `x`, `y`, and `z` represent voxel coordinates in the image's own data matrix.

Based on this principle, SPM's reslice function can be used to change the size of AAL3: black margins are padded for smaller AAL images, and black margins are cropped for larger AAL images, achieving coordinate alignment without affecting the PET image itself. Run `Reslice_ROI.m` to generate an AAL3 template adapted to the PET size: `Reslice_aal3.nii`. Then use the new brain-region template for calculation.

### 3. Calculate Feature Values
`PET_Intensity.py` can calculate feature values for each brain region. Modify the following parameters:

1. `ROI`: the resized AAL template
2. `PET`: the PET image path
3. `prefix='wr'`: corresponds to the PET registration prefix
4. `subject_Info`: the CSV file downloaded with the images, containing subject information
5. `roi_csv`: the file used to store ROI calculation results

## Step 6: PET Skull Removal and Smoothing
The main purpose is to obtain PET image data that can be used for deep neural network training.

### 1. Skull Removal
Use the skull-stripped MRI image directly as `i1`, and set the PET image requiring skull removal as `i2`. The principle is to use the expression `i2.*(i1>0)` to remove non-brain tissue from the PET image.

SPM's ImCalc can be used for this mask calculation, allowing PET skull stripping based on the MRI skull-stripping result while keeping other image regions unaffected.

The above process is implemented as the batch-processing script `PET_batch_skull_separation.m`. Set the parameters in this batch-processing script before running it.


### 2. Gaussian Smoothing
Use SPM's Smooth module and set the Gaussian smoothing kernel to 6 mm.

The batch-processing script is `PET_Smooth.m`.
