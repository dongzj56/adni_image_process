'''
Running this code can either use the nibabel library for image registration and spatial transformation
'''
import os
import numpy as np
import nibabel as nib
from scipy.ndimage import gaussian_filter
import SimpleITK as sitk
import glob

def auto_reorient(p, i_type='t1', center_origin=True, log_file='Failed_auto_reorient.txt'):
    # Define the template path. Adjust this according to the actual SPM path.
    spm_path = r'C:\spm&cat\spm12'  # Replace this with the actual SPM installation path.
    templates = {
        't1': os.path.join(spm_path, 'toolbox', 'OldNorm', 'T1.nii'),
        't2': os.path.join(spm_path, 'toolbox', 'OldNorm', 'T2.nii'),
        'epi': os.path.join(spm_path, 'toolbox', 'OldNorm', 'EPI.nii'),
        'pet': os.path.join(spm_path, 'toolbox', 'OldNorm', 'PET.nii'),
        't1canonical': os.path.join(spm_path, 'canonical', 'single_subj_T1.nii')
    }
    tmpl = templates.get(i_type.lower(), templates['t1'])
    
    # Initialize the log file.
    num_err = 0
    num_done = 0
    with open(log_file, 'w') as fid:
        for file_path in p:
            try:
                # Move the origin to the image center.
                if center_origin:
                    img = nib.load(file_path)
                    dim = img.header['dim'][1:4]
                    new_affine = img.affine.copy()
                    new_affine[:3, 3] = -np.dot(new_affine[:3, :3], (np.array(dim) - 1) / 2)
                    nib.save(nib.Nifti1Image(img.get_fdata(), new_affine), file_path)
                
                # Smooth the image.
                smoothed_data = gaussian_filter(img.get_fdata(), sigma=12)
                temp_path = 'temp.nii'
                nib.save(nib.Nifti1Image(smoothed_data, img.affine), temp_path)
                
                # Run rigid registration with SimpleITK.
                fixed_image = sitk.ReadImage(tmpl)
                moving_image = sitk.ReadImage(temp_path)
                
                # Initialize the registration method.
                registration_method = sitk.ImageRegistrationMethod()
                registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
                registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100)
                registration_method.SetInitialTransform(sitk.CenteredTransformInitializer(
                    fixed_image, moving_image, sitk.Euler3DTransform()))
                
                # Run registration.
                final_transform = registration_method.Execute(fixed_image, moving_image)
                
                # Apply the transform to the original image.
                img = nib.load(file_path)
                transform_matrix = np.eye(4)
                transform_matrix[:3, :3] = np.array(final_transform.GetMatrix()).reshape(3,3)
                transform_matrix[:3, 3] = final_transform.GetTranslation()
                new_affine = transform_matrix @ img.affine
                
                # Save the reoriented image.
                nib.save(nib.Nifti1Image(img.get_fdata(), new_affine), file_path)
                num_done += 1
                print(f'Processed {num_done}/{len(p)} files')
            
            except Exception as e:
                num_err += 1
                fid.write(f'Failed: {file_path}\nError: {str(e)}\n{"="*20}\n')
                print(f'Failed: {file_path}')
    
    print(f'Success: {len(p)-num_err}, Failed: {num_err}')
    if os.path.exists('temp.nii'):
        os.remove('temp.nii')

if __name__ == "__main__":
    # Get all .nii files. Replace this with the actual path.
    file_list = glob.glob(r'C:\Users\dongz\Desktop\ADNI_Image_MRI\ADNI')  
    
    # Run reorientation.
    auto_reorient(file_list, i_type='t1', center_origin=True)
