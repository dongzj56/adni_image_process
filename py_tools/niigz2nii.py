import os
import gzip
import shutil

def decompress_nii_gz(input_dir):
    """
    解压目录下所有.nii.gz文件为.nii文件
    :param input_dir: 输入目录路径
    """
    # 遍历目录下所有文件
    for filename in os.listdir(input_dir):
        if filename.endswith(".nii.gz"):
            # 构造完整输入路径
            gz_path = os.path.join(input_dir, filename)
            
            # 构造输出文件名（去掉.gz后缀）
            nii_filename = filename[:-3]  # 移除最后的3个字符（.gz）
            nii_path = os.path.join(input_dir, nii_filename)
            
            # 解压文件
            try:
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(nii_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"已解压: {filename} -> {nii_filename}")
            except Exception as e:
                print(f"解压失败: {filename} | 错误: {str(e)}")

if __name__ == "__main__":
    target_dir = input("请输入目录路径: ").strip()
    
    if os.path.exists(target_dir) and os.path.isdir(target_dir):
        decompress_nii_gz(target_dir)
        print("解压完成！")
    else:
        print("错误：目录不存在或路径无效")