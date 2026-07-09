import datetime
import os
import time

from tqdm import tqdm
import SimpleITK as sitk


def correct_bias_field(input_image_path, output_image_path, shrink_factor=1, mask_image_path=None,
                       iterations=0, fitting_levels=4):
    """Apply N4 bias-field correction to the specified image."""

    # Read the input image as float32.
    input_image = sitk.ReadImage(input_image_path, sitk.sitkFloat32)

    # Read the mask image if a mask path is provided.
    if mask_image_path:
        mask_image = sitk.ReadImage(mask_image_path, sitk.sitkUInt8)
    else:
        # If no mask is provided, generate one with Otsu thresholding.
        mask_image = sitk.OtsuThreshold(input_image, 0, 1, 200)

    # Shrink the input image and mask according to the shrink factor.
    image = input_image
    if shrink_factor > 1:
        image = sitk.Shrink(input_image, [shrink_factor] * input_image.GetDimension())
        mask_image = sitk.Shrink(mask_image, [shrink_factor] * input_image.GetDimension())

    # Create the N4 bias-field corrector.
    corrector = sitk.N4BiasFieldCorrectionImageFilter()
    # Update fitting levels if an iteration count is provided.
    if iterations:
        corrector.SetMaximumNumberOfIterations([int(iterations)] * fitting_levels)

    # Run bias-field correction.
    corrected_image = corrector.Execute(image, mask_image)

    # Get the corrected bias-field image.
    log_bias_field = corrector.GetLogBiasFieldAsImage(input_image)

    # Restore the full-resolution image using the bias-field correction image.
    corrected_image_full_resolution = input_image / sitk.Exp(log_bias_field)

    # Write the full-resolution corrected image.
    sitk.WriteImage(corrected_image_full_resolution, output_image_path)

    # If the shrink factor is greater than 1, write the shrunk corrected image.
    if shrink_factor > 1:
        sitk.WriteImage(corrected_image, "Python-Example-N4BiasFieldCorrection-shrunk.nrrd")


def batch_N4(in_folder, out_folder, endswith):
    log_file = r'.\N4_Error_Log.txt'

    shrink_factor = 1  # Optional shrink factor.
    mask_image_path = None  # Optional mask image path. Use None to apply Otsu thresholding.
    number_of_iterations = 0  # Optional iteration count.
    number_of_fitting_levels = 4  # Optional number of fitting levels.
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    for file_name in tqdm(os.listdir(in_folder), desc="Processing files"):
        if file_name.lower().endswith(tuple(endswith)):  # Detect files with the configured suffix.
            in_file = os.path.join(in_folder, file_name)
            out_file = os.path.join(out_folder, file_name)

            print('\n',"=" * 100)
            print("In: ", in_file)
            print("Out: ", out_file)
            try:
                # Call the function to run bias-field correction.
                correct_bias_field(in_file, out_file, shrink_factor, mask_image_path,
                                   number_of_iterations, number_of_fitting_levels)
            except Exception as e:
                with open(log_file, 'a') as f:
                    f.write(f"Error processing file {in_file}\n: {str(e)}\n")
                print(f"Error occurred during bias field correction:\n {in_file}")


if __name__ == "__main__":
    in_folder = rf"C:\Users\dongzj\Desktop\mri1"
    out_folder = rf"C:\Users\dongzj\Desktop\mri1\out_test"
    endswith = tuple('.nii')
    batch_N4(in_folder, out_folder, endswith)

    # ADNI = 'ADNI1'
    # Pre_Path = rf'D:\Matlab\Project\GroupMeeting'
    # out_folder = \
    #     rf"{Pre_Path}\Datasets_Filter_From_Raw\{ADNI}\N4"
    # AC_PC_Root = \
    #     rf"{Pre_Path}\Datasets_Filter_From_Raw\{ADNI}\AC-PC"
    # endswith = tuple('.nii')
    # Modality = ['MRI', 'PET']
    # # Record the start time.
    # start_time = time.time()
    # print("Trying to use SimpleITK for bias field correction, which may take longer.")
    #
    # for m in Modality:
    #     in_folder = os.path.join(AC_PC_Root, m)
    #     m_out_folder = os.path.join(out_folder, m)
    #     if not os.path.exists(m_out_folder):
    #         os.makedirs(m_out_folder)
    #     batch_N4(in_folder, m_out_folder, endswith)
    # end_time = time.time()
    # # Compute the runtime.
    # duration = end_time - start_time
    # print("Bias-field correction complete.")
    #
    # formatted_duration = str(datetime.timedelta(seconds=duration))
    # print(f"Runtime: {formatted_duration}")
