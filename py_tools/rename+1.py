import os

def add_prefix_to_files(directory: str, prefix: str) -> None:
    """
    Rename all files in the specified directory by adding a prefix.
    Only regular files are processed; subdirectories are not affected.
    """
    for name in os.listdir(directory):
        old_path = os.path.join(directory, name)
        # To include subdirectories, change this to os.path.isfile(old_path) or os.path.isdir(old_path).
        if os.path.isfile(old_path):
            new_name = f"{prefix}{name}"
            new_path = os.path.join(directory, new_name)
            # If the target already exists, decide here whether to overwrite, skip, or rename.
            os.rename(old_path, new_path)
            print(f"{name}  →  {new_name}")

if __name__ == "__main__":
    # === Change these to your own directory and prefix. ===
    dir_path = rf"F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\04PET_normalized\MNI_1mm"   # Target folder.
    prefix   = "normal_"                              # Prefix to add before each filename.
    # ==================================
    add_prefix_to_files(dir_path, prefix)
