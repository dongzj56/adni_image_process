import gzip
from pathlib import Path

def compress_nii_files(directory):
    """
    压缩指定目录下的所有.nii文件为.nii.gz格式（无损压缩）
    参数:
        directory (str): 目标目录路径
    """
    base_dir = Path(directory)
    
    # 遍历目录下所有.nii文件
    for nii_file in base_dir.glob('*.nii'):
        if not nii_file.is_file():
            continue  # 跳过非文件对象（如目录）
        
        # 构造压缩文件路径
        gz_path = nii_file.with_suffix('.nii.gz')
        
        # 分块读写以支持大文件
        with open(nii_file, 'rb') as f_in, gzip.open(gz_path, 'wb') as f_out:
            while chunk := f_in.read(4096 * 1024):  # 每次读取4MB，减少内存占用
                f_out.write(chunk)
        
        print(f"Compression complete: {nii_file.name} -> {gz_path.name}")

if __name__ == "__main__":
    target_dir = input("Please enter the destination directory path: ").strip()
    compress_nii_files(target_dir)