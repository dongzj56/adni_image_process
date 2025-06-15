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
    # 定义模板路径（需要根据实际SPM路径调整）
    spm_path = 'C:\spm&cat\spm12'  # 需替换为实际的SPM安装路径
    templates = {
        't1': os.path.join(spm_path, 'toolbox', 'OldNorm', 'T1.nii'),
        't2': os.path.join(spm_path, 'toolbox', 'OldNorm', 'T2.nii'),
        'epi': os.path.join(spm_path, 'toolbox', 'OldNorm', 'EPI.nii'),
        'pet': os.path.join(spm_path, 'toolbox', 'OldNorm', 'PET.nii'),
        't1canonical': os.path.join(spm_path, 'canonical', 'single_subj_T1.nii')
    }
    tmpl = templates.get(i_type.lower(), templates['t1'])
    
    # 初始化日志文件
    num_err = 0
    num_done = 0
    with open(log_file, 'w') as fid:
        for file_path in p:
            try:
                # 调整原点至图像中心
                if center_origin:
                    img = nib.load(file_path)
                    dim = img.header['dim'][1:4]
                    new_affine = img.affine.copy()
                    new_affine[:3, 3] = -np.dot(new_affine[:3, :3], (np.array(dim) - 1) / 2)
                    nib.save(nib.Nifti1Image(img.get_fdata(), new_affine), file_path)
                
                # 图像平滑
                smoothed_data = gaussian_filter(img.get_fdata(), sigma=12)
                temp_path = 'temp.nii'
                nib.save(nib.Nifti1Image(smoothed_data, img.affine), temp_path)
                
                # 使用SimpleITK进行刚性配准
                fixed_image = sitk.ReadImage(tmpl)
                moving_image = sitk.ReadImage(temp_path)
                
                # 初始化配准方法
                registration_method = sitk.ImageRegistrationMethod()
                registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
                registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100)
                registration_method.SetInitialTransform(sitk.CenteredTransformInitializer(
                    fixed_image, moving_image, sitk.Euler3DTransform()))
                
                # 执行配准
                final_transform = registration_method.Execute(fixed_image, moving_image)
                
                # 应用变换到原始图像
                img = nib.load(file_path)
                transform_matrix = np.eye(4)
                transform_matrix[:3, :3] = np.array(final_transform.GetMatrix()).reshape(3,3)
                transform_matrix[:3, 3] = final_transform.GetTranslation()
                new_affine = transform_matrix @ img.affine
                
                # 保存重新定向后的图像
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
    # 获取所有.nii文件（需要修改为实际路径）
    file_list = glob.glob('C:\Users\dongz\Desktop\ADNI_Image_MRI\ADNI')  
    
    # 运行重定向
    auto_reorient(file_list, i_type='t1', center_origin=True)