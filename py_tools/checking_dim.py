import nibabel as nib
import os
import glob

def check_nifti_dimensions(directory):
    """
    Check the dimension information of all NIfTI files in the specified directory.
    """
    # Get all .nii and .nii.gz files.
    file_list = glob.glob(os.path.join(directory, "*.nii")) + \
                glob.glob(os.path.join(directory, "*.nii.gz"))

    if not file_list:
        print("No NIfTI files found")
        return

    dimension_records = {}
    problem_files = []

    print("Checking NIfTI file dimensions...\n")
    
    for file_path in file_list:
        try:
            # Load the NIfTI file.
            img = nib.load(file_path)
            dim = img.header['dim'][1:5]  # Get the first four dimensions, usually 3D space plus time.
            dim = tuple(map(int, dim))    # Convert to an integer tuple.
            
            # Record dimension information.
            if dim not in dimension_records:
                dimension_records[dim] = []
            dimension_records[dim].append(os.path.basename(file_path))
            
            print(f"File: {os.path.basename(file_path):<30} Dimensions: {dim}")
            
        except Exception as e:
            problem_files.append((file_path, str(e)))
            print(f"Could not read file: {os.path.basename(file_path)} - Error: {str(e)}")

    # Print summary report.
    print("\n==== Dimension Summary ====")
    for idx, (dim, files) in enumerate(dimension_records.items(), 1):
        print(f"{idx}. Dimension {dim}: {len(files)} files")
        print("   Example files: " + ", ".join(files[:3]) + ("..." if len(files)>3 else ""))

    # Show problem files.
    if problem_files:
        print("\n==== Problem Files ====")
        for idx, (path, err) in enumerate(problem_files, 1):
            print(f"{idx}. {os.path.basename(path)} - Error: {err}")

if __name__ == "__main__":
    target_dir = input("Enter the directory path to check: ").strip()
    
    if not os.path.isdir(target_dir):
        print("Error: the specified path does not exist or is not a directory")
    else:
        check_nifti_dimensions(target_dir)
