'''
This code is used to convert dcm files in all image data to nii format
'''
import os
import subprocess

root_dir = rf'C:\Users\dongzj\Desktop\MRI-MCI\ADNI'
result_dict = {}

# Traverse all folders in the root directory
for folder_entry in os.scandir(root_dir):
    if folder_entry.is_dir():
        folder_name = folder_entry.name
        folder_result = False  # Default set to False
        
        # Traverse files in the folder and determine the file type
        for file_entry in os.scandir(folder_entry.path):
            if file_entry.is_file():

                print(file_entry)

                file_lower = file_entry.name.lower()
                if file_lower.endswith(('.nii', '.nii.gz')):
                    folder_result = True  # If it's a NIfTI file, set it to True
                    break  # Stop checking once a NIfTI file is found
                elif file_lower.endswith('.dcm'):
                    folder_result = False  # If it's a DICOM file, set it to False
                    break  # Stop checking once a DICOM file is found
        
        # Add the folder name and result to the dictionary
        result_dict[folder_name] = folder_result

# Count the number of keys with True and False values
true_count = sum(1 for value in result_dict.values() if value is True)
false_count = sum(1 for value in result_dict.values() if value is False)

# Output the count of True and False values
print(f"\nNumber of True: {true_count}")
print(f"Number of False: {false_count}")

print('dcm to nii...')

def Single_Dicom2Nii(DICOM_Dir, Nii_Dir):
    """
    Convert DICOM files to NIfTI format

    Parameters:
    DICOM_Dir: The directory path of DICOM files to be converted
    Nii_Dir: The directory path for output NIfTI files
    """
    
    dcm2niix_path = r'tools\dcm2niix.exe'
    # Output NIfTI directory
    filename_format = '%i'  # File name format
    bids_sidecar = 'y'  # Generate BIDS sidecar JSON files
    philips_scaling = 'y'  # Enable Philips exact floating-point scaling
    bids_anonymize = 'n'  # Anonymize BIDS sidecar files (y: Yes, n: No)
    include_patient_details = 'n'  # Generate file with patient details (txt)
    write_behavior = '1'  # Write behavior for name conflicts (0=skip, 1=overwrite, 2=add suffix)
    zip2gz = 'n'

    # Construct dcm2niix command
    command = [
        dcm2niix_path,  # Path to dcm2niix executable
        '-f', filename_format,  # File name format
        '-o', Nii_Dir,  # Output directory
        '-p', philips_scaling,  # Philips exact floating-point scaling
        '-t', include_patient_details,  # Include patient details
        '-b', bids_sidecar,  # Generate BIDS sidecar files
        '-ba', bids_anonymize,  # Anonymize BIDS sidecar files
        '-w', write_behavior,  # Write behavior for name conflicts
        '-z', zip2gz,
        '-d', 'myInstanceNumberOrderIsNotSpatial',  # Separate -D and parameter
        DICOM_Dir  # Input folder
    ]
    try:
        # Call dcm2niix to convert
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("=" * 100)
        print(result.stdout.decode())  # Output standard output
        print(f"Converted DICOM files {str(DICOM_Dir)} to NIfTI format.")
    except subprocess.CalledProcessError as e:
        print("=" * 100)
        err = e.stderr.decode().strip()
        out = e.stdout.decode().strip()
        print(f"Error/Warning in {str(DICOM_Dir)}\n{err}\n{out}\n")  # Output error messages


count = 0

# Traverse the dictionary and process all folders with False values
for folder_name, is_nii in result_dict.items():
    if not is_nii:  # If the value is False
        count = count +1
        folder_path = os.path.join(root_dir, folder_name)
        Single_Dicom2Nii(folder_path,folder_path)  # Pass the folder path to dcm2nii function for processing
        print(f'The {count}th conversion is complete:', folder_name)
