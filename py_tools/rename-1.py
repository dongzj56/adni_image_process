'''Rename all files in a directory by removing a filename prefix.'''
import os
import shutil

# Get the directory path from user input.
directory = input("Enter directory path: ")
# Remove possible quotes.
directory = directory.strip('"').strip("'")

# Get the number of leading characters to remove.
try:
    remove_length = int(input("Enter the number of leading characters to remove from filenames: "))
    if remove_length < 0:
        print("The character length must be a positive integer. Using default value 0.")
        remove_length = 0
except ValueError:
    print("Invalid input. Using default value 0.")
    remove_length = 0

# Ensure the directory exists.
if not os.path.exists(directory):
    print(f"Directory {directory} does not exist.")
else:
    # Iterate over all files in the directory.
    for filename in os.listdir(directory):
        # Get the full file path.
        file_path = os.path.join(directory, filename)
        
        # Check whether this is a file rather than a directory.
        if os.path.isfile(file_path):
            # Remove leading characters if the filename is long enough.
            if len(filename) > remove_length:
                new_filename = filename[remove_length:]
                new_file_path = os.path.join(directory, new_filename)
                
                
                # Rename the file.
                try:
                    shutil.move(file_path, new_file_path)
                    print(f"Renamed: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"Error renaming {filename}: {e}")
            else:
                print(f"Skipped {filename}: filename is too short")
    
    print("Rename operation complete.")
