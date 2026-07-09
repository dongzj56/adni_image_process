import gzip
from pathlib import Path

def compress_nii_files(directory):
    """
    Compress all .nii files in the specified directory to .nii.gz format.
    Args:
        directory (str): Target directory path.
    """
    base_dir = Path(directory)
    
    # Iterate over all .nii files in the directory.
    for nii_file in base_dir.glob('*.nii'):
        if not nii_file.is_file():
            continue  # Skip non-file objects, such as directories.
        
        # Build the compressed output path.
        gz_path = nii_file.with_suffix('.nii.gz')
        
        # Read and write in chunks to support large files.
        with open(nii_file, 'rb') as f_in, gzip.open(gz_path, 'wb') as f_out:
            while chunk := f_in.read(4096 * 1024):  # Read 4 MB each time to reduce memory use.
                f_out.write(chunk)
        
        print(f"Compression complete: {nii_file.name} -> {gz_path.name}")

if __name__ == "__main__":
    target_dir = input("Please enter the destination directory path: ").strip()
    compress_nii_files(target_dir)
