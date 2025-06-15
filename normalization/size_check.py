import os
import nibabel as nib
from tqdm import tqdm

def check_nii_files(directory, expected_shape=(112, 136, 112)):
    """
    检查目录下所有NIfTI文件的完整性和形状
    
    参数:
    directory (str): 要检查的目录路径
    expected_shape (tuple): 预期的图像尺寸，默认为(113, 137, 113)
    
    返回:
    dict: 包含有效文件和无效文件的字典
    """
    results = {
        'valid': [],
        'invalid': [],
        'errors': []
    }
    
    # 获取目录下所有.nii文件
    nii_files = [f for f in os.listdir(directory) if f.endswith('.nii')]
    
    print(f"发现 {len(nii_files)} 个NIfTI文件")
    print(f"预期形状: {expected_shape}")
    
    # 使用tqdm显示进度条
    for filename in tqdm(nii_files, desc="检查文件"):
        file_path = os.path.join(directory, filename)
        
        try:
            # 尝试加载文件
            img = nib.load(file_path)
            
            # 检查文件大小是否合理
            # 计算预期大小 (假设为float32数据类型)
            expected_size = expected_shape[0] * expected_shape[1] * expected_shape[2] * 4  # float32 = 4 bytes
            actual_size = os.path.getsize(file_path)
            
            # 检查形状是否符合预期
            if img.shape == expected_shape and actual_size >= expected_size * 0.9:  # 允许10%的误差
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
    # 指定要检查的目录
    directory = rf'C:\Users\dongz\Desktop\adni_dataset\MRI_GM_113_137_113-1'
    
    # 执行检查
    results = check_nii_files(directory)
    
    # 输出结果
    print("\n===== 检查结果 =====")
    print(f"有效文件: {len(results['valid'])}")
    print(f"无效文件: {len(results['invalid'])}")
    print(f"错误文件: {len(results['errors'])}")
    
    # 保存结果到文件
    with open('nii_check_results.txt', 'w') as f:
        f.write("===== 有效文件 =====\n")
        for filename in results['valid']:
            f.write(f"{filename}\n")
            
        f.write("\n===== 无效文件 =====\n")
        for item in results['invalid']:
            f.write(f"{item['filename']}: 形状={item['shape']}, 大小={item['size']}/{item['expected_size']}字节\n")
            
        f.write("\n===== 错误文件 =====\n")
        for item in results['errors']:
            f.write(f"{item['filename']}: {item['error']}\n")
    
    print("结果已保存到 nii_check_results.txt")

if __name__ == "__main__":
    main()