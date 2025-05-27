'''
After the image is fully converted to nii format, run this code 
to modify the path format again for easy integration and loading
'''

import os
import shutil

def find_id_dirs(root_dir):
    """Find all ID directories under the root directory."""
    return [entry.path for entry in os.scandir(root_dir) if entry.is_dir()]

def process_id_dir(id_dir, root_dir):
    """Process a single ID directory: Move and rename .nii files."""
    id_name = os.path.basename(id_dir)
    
    # Traverse all subdirectories to find .nii files
    for root, _, files in os.walk(id_dir, topdown=False):
        for file in files:
            if file.lower().endswith('.nii'):
                src_path = os.path.join(root, file)
                
                # Construct the destination path and handle naming conflicts
                base_name = f"{id_name}.nii"
                dest_path = os.path.join(root_dir, base_name)
                counter = 1
                while os.path.exists(dest_path):
                    base_name = f"{id_name}_{counter}.nii"
                    dest_path = os.path.join(root_dir, base_name)
                    counter += 1
                
                # Move the file
                shutil.move(src_path, dest_path)
                print(f"Moved: {src_path} -> {dest_path}")

def delete_all_dirs(root_dir):
    """Delete all directories under the root directory (regardless of whether they are empty)."""
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            try:
                shutil.rmtree(entry.path)  # Recursively delete the directory
                print(f"Deleted directory: {entry.path}")
            except Exception as e:
                print(f"Error deleting {entry.path}: {str(e)}")

if __name__ == '__main__':
    root_dir = rf"C:\Users\dongzj\Desktop\MRI-MCI\ADNI"
    id_dirs = find_id_dirs(root_dir)
    print(f"Found {len(id_dirs)} ID directories")
    
    for idx, id_dir in enumerate(id_dirs, 1):
        print(f"Processing {idx}/{len(id_dirs)}: {os.path.basename(id_dir)}")
        process_id_dir(id_dir, root_dir)
    
    # Delete all directories under the root directory
    delete_all_dirs(root_dir)
    
    print("\nAll files have been reorganized and all directories deleted successfully!")