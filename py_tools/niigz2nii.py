import os
import gzip
import shutil

def decompress_nii_gz(input_dir):
    """
    Decompress all .nii.gz files in a directory to .nii files.
    :param input_dir: Input directory path.
    """
    # Iterate over all files in the directory.
    for filename in os.listdir(input_dir):
        if filename.endswith(".nii.gz"):
            # Build the full input path.
            gz_path = os.path.join(input_dir, filename)
            
            # Build the output filename by removing the .gz suffix.
            nii_filename = filename[:-3]  # Remove the final three characters (.gz).
            nii_path = os.path.join(input_dir, nii_filename)
            
            # Decompress the file.
            try:
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(nii_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"Decompressed: {filename} -> {nii_filename}")
            except Exception as e:
                print(f"Decompression failed: {filename} | Error: {str(e)}")

if __name__ == "__main__":
    target_dir = input("Enter directory path: ").strip()
    
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        decompress_nii_gz(target_dir)
        print("Decompression complete.")
    else:
        print("Error: directory does not exist or path is invalid")
