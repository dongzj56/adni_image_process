import os
import numpy as np
import SimpleITK as sitk
import csv

import pandas as pd
from tqdm import tqdm

def load_roi_info(roi_csv, header=False, delimiter=' '):
    """
    Load ROI information from a CSV file.
    Returns a dictionary whose key is the ROI value and whose value is (ROIid, ROIabbr, ROIname).
    """
    roi_info = {}
    with open(roi_csv, mode='r') as file:
        reader = csv.reader(file, delimiter=delimiter)
        if header:
            next(reader)  # Skip the header.
        for row in reader:
            roi_value = int(row[0])
            if len(row) <= 2:
                row.append(row[0])
            roi_info[roi_value] = (roi_value, row[1], row[2])
    return roi_info

def get_header(roi_info,Vox_mm3,SUVr):
    # Build the CSV header.
    header = ['Subject']
    for v in roi_info.keys():
        header.append(roi_info[v][1])
        if Vox_mm3:
            header.append(roi_info[v][1] + '_Vox_mm3')
        if SUVr:
            header.append(roi_info[v][1] + '_SUVr')
    return header

def get_pet_data(mask_path, nii_dir, output_csv, startswith='r', cerebellar=False, Vox_mm3=True, roi_info=None, subject_info=None, SUVr=False):
    print('Initializing...')
    ID = 'Subject ID'
    Injected_dose = 185  # MBq, FDG-PET reference in ADNI.
    cerebellar_ID = []  # 95~120
    s_info = None
    if SUVr:
        if subject_info:
            s_info = pd.read_csv(subject_info)
            s_info = s_info[s_info['Modality'] == 'PET']
            # Calculate SUVr normalized by the cerebellum. AAL3 cerebellar regions are:
            cerebellar_ID = np.arange(95, 121)  # 95~120
            # cerebellar_ID = np.arange(95, 113)  # 95~112
        else:
            print("Calculating the SUVr must input the subject_info(Weight) parameter")
            return



    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        write_header = False
        # Get .nii or .nii.gz files.
        nii_files = [f for f in os.listdir(nii_dir) if
                     (f.endswith('.nii') or f.endswith('.nii.gz')) and f.startswith(startswith)]


        # Read the mask file and get unique values.
        mask = sitk.ReadImage(mask_path)
        mask_array = sitk.GetArrayFromImage(mask)
        unique_values = np.unique(mask_array)[np.unique(mask_array) != 0]  # Exclude 0.

        # Create a dictionary to store the indices for each value.
        indices_dict = {}
        for value in unique_values:
            indices = np.argwhere(mask_array == value)  # Get indices for each value.
            indices_dict[value] = indices  # Save the indices in the dictionary.

        # Check whether ROI length and mask length are consistent.
        if roi_info and len(unique_values) != len(roi_info) :
            print(f"\nROI_INFO length ({len(roi_info)}) and "
                  f"ROI.nii length ({len(unique_values)}) are inconsistent; unmatched ROI values will be 0")
        if roi_info is None:
            roi_info = {}
            for uv in unique_values:
                roi_info[uv] = (uv, 'ROI_'+str(uv), uv)
        header = get_header(roi_info,Vox_mm3,SUVr)
        writer.writerow(header)

        for nii_filename in tqdm(nii_files, desc="Processing NIfTI Files", unit="file"):
            ce_suv = 1
            weight = -1

            nii_path = os.path.join(nii_dir, nii_filename)
            nii = sitk.ReadImage(nii_path)
            nii_array = sitk.GetArrayFromImage(nii)

            sid, _ = os.path.splitext(nii_filename)
            sid = sid[len(startswith):]
            # sid = sid.removeprefix(startswith)

            if SUVr:
                weight_ = s_info[s_info[ID] == sid]['Weight']
                if len(weight_) >0:
                    weight = float(weight_.iloc[0]) * 1000
                else:
                    print(f'{sid} have not weight, SUVr May be 0')
                sum_ce = 0
                for ci in cerebellar_ID:
                    # Get all indices in the template that equal the current value.
                    indices = indices_dict[ci]
                    # ce_vox_num = len(indices)
                    ce_vox_in = nii_array[tuple(indices.T)]  # Transpose indices to match NumPy indexing.
                    # sum_ce += np.mean(ce_vox_in)
                    sum_ce += np.sum(ce_vox_in)
                if weight !=0:
                    ce_suv = sum_ce/(Injected_dose/weight)
                else:
                    weight = 80
                    ce_suv = sum_ce/(Injected_dose/weight)

            average_values = []
            Null_ROI = []
            for value in roi_info.keys():
                avg_intensity = 0
                vox_mm3 = 0
                roi_suvr = 0
                if (value not in unique_values):
                    Null_ROI.append(value)
                if (value not in unique_values) or (value in cerebellar_ID and not cerebellar):
                    pass
                else: # value in unique_values
                    # Get all indices in the template that equal the current value.
                    indices = indices_dict[value]
                    intensity = nii_array[tuple(indices.T)]  # Transpose indices to match NumPy indexing.
                    avg_intensity = np.mean(intensity)
                    if SUVr:
                        sum_intensity = np.sum(intensity)
                        roi_suv = sum_intensity/(Injected_dose/weight) if weight != -1 else 0
                        roi_suvr = roi_suv/ce_suv
                    vox_mm3 = len(indices)

                average_values.append(str(avg_intensity))
                if Vox_mm3:
                    average_values.append(str(vox_mm3))
                if SUVr:
                    average_values.append(str(roi_suvr))

            writer.writerow([sid] + average_values)
        print(f"Results written to CSV file: {output_csv}")
        print('Invalid ROI indices:',Null_ROI)


if __name__ == '__main__':
    # Usage example.
    ROI = r'tools\Reslice_aal3.nii' # ROI path.
    PET = rf'C:\Users\dongz\Desktop\adni_dataset\petjisuan'  # Directory for registered and normalized PET images.
    prefix = ''  # Corresponds to the registered PET filename prefix, for example wr for files starting with wr.
    # subject_Info is the CSV information file used when filtering data.
    subject_Info = rf'PET_processed.csv'
    roi_csv = 'tools/aal3.csv'  # ROI information file path.
    ROI_INFO = load_roi_info(roi_csv, header=True, delimiter=';')

    output_csv = 'PET_DATA.csv'  # Output CSV file path.
    # Besides intensity, configure whether to calculate cerebellar values, ROI volume, and SUVr.
    # SUVr requires subject_info containing patient weight.
    get_pet_data(ROI, PET, output_csv, startswith=prefix, cerebellar=True,
                 Vox_mm3=False, roi_info=ROI_INFO, subject_info=subject_Info, SUVr=True)

