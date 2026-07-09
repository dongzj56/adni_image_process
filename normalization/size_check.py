import os
import nibabel as nib
from tqdm import tqdm

def check_nii_files(directory, expected_shape=(112, 136, 112)):
    """
    Check the integrity and shape of all NIfTI files in a directory.
    
    Args:
    directory (str): Directory path to check.
    expected_shape (tuple): Expected image shape. Defaults to (113, 137, 113).
    
    Returns:
    dict: Dictionary containing valid, invalid, and error files.
    """
    results = {
        'valid': [],
        'invalid': [],
        'errors': []
    }
    
    # Get all .nii files in the directory.
    nii_files = [f for f in os.listdir(directory) if f.endswith('.nii')]
    
    print(f"Found {len(nii_files)} NIfTI files")
    print(f"Expected shape: {expected_shape}")
    
    # Show progress with tqdm.
    for filename in tqdm(nii_files, desc="Checking files"):
        file_path = os.path.join(directory, filename)
        
        try:
            # Try loading the file.
            img = nib.load(file_path)
            
            # Check whether the file size is reasonable.
            # Compute the expected size assuming float32 data.
            expected_size = expected_shape[0] * expected_shape[1] * expected_shape[2] * 4  # float32 = 4 bytes
            actual_size = os.path.getsize(file_path)
            
            # Check whether the shape matches the expected shape.
            if img.shape == expected_shape and actual_size >= expected_size * 0.9:  # Allow a 10% tolerance.
                results['valid'].append(filename)
            else:
                results['invalid'].append({
                    'filename': filename,
                    'shape': img.shape,
                    'size': actual_size,
                    'expected_size': expected_size
                })
                
        except Exception as e:
            results['errors'].append({
                'filename': filename,
                'error': str(e)
            })
    
    return results

def main():
    # Directory to check.
    directory = rf'C:\Users\dongz\Desktop\adni_dataset\MRI_GM_113_137_113-1'
    
    # Run checks.
    results = check_nii_files(directory)
    
    # Print results.
    print("\n===== Check Results =====")
    print(f"Valid files: {len(results['valid'])}")
    print(f"Invalid files: {len(results['invalid'])}")
    print(f"Error files: {len(results['errors'])}")
    
    # Save results to a file.
    with open('nii_check_results.txt', 'w') as f:
        f.write("===== Valid Files =====\n")
        for filename in results['valid']:
            f.write(f"{filename}\n")
            
        f.write("\n===== Invalid Files =====\n")
        for item in results['invalid']:
            f.write(f"{item['filename']}: shape={item['shape']}, size={item['size']}/{item['expected_size']} bytes\n")
            
        f.write("\n===== Error Files =====\n")
        for item in results['errors']:
            f.write(f"{item['filename']}: {item['error']}\n")
    
    print("Results saved to nii_check_results.txt")

if __name__ == "__main__":
    main()
