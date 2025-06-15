import os
import nibabel as nib

# 设置需要检查的目录路径（替换成你的目标目录）
target_dir = "D:\ADNI_PET\ADNI"

# 遍历目录中的所有文件
for filename in os.listdir(target_dir):
    # 检查文件扩展名是否为NIfTI格式
    if filename.endswith((".nii", ".nii.gz")):
        file_path = os.path.join(target_dir, filename)
        
        try:
            # 加载NIfTI文件（仅读取头信息以节省内存）
            img = nib.load(file_path)
            
            # 检查维度是否为4D
            if len(img.shape) == 4:
                print(f"4D image found: {filename}")
                
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")