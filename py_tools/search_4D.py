import os
import nibabel as nib

# Directory path to check. Replace this with your target directory.
target_dir = r"D:\ADNI_PET\ADNI"

# Iterate over all files in the directory.
for filename in os.listdir(target_dir):
    # Check whether the file extension is a NIfTI format.
    if filename.endswith((".nii", ".nii.gz")):
        file_path = os.path.join(target_dir, filename)
        
        try:
            # Load the NIfTI file, reading only header information to save memory.
            img = nib.load(file_path)
            
            # Check whether the image is 4D.
            if len(img.shape) == 4:
                print(f"4D image found: {filename}")
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
