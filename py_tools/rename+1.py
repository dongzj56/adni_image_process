import os

def add_prefix_to_files(directory: str, prefix: str) -> None:
    """
    给指定目录下的所有文件重命名，在原文件名之前添加 prefix。
    仅处理普通文件；子目录不受影响。
    """
    for name in os.listdir(directory):
        old_path = os.path.join(directory, name)
        # 如果需要同时处理子目录，可改成 os.path.isfile(old_path) or os.path.isdir(old_path)
        if os.path.isfile(old_path):
            new_name = f"{prefix}{name}"
            new_path = os.path.join(directory, new_name)
            # 若目标文件已存在，可在这里决定覆盖 / 跳过 / 改名
            os.rename(old_path, new_path)
            print(f"{name}  →  {new_name}")

if __name__ == "__main__":
    # === 修改成你自己的目录和前缀 ===
    dir_path = rf"F:\ADNI数据集902样本\05-MRI头骨分离\p0original_MNI\MRI"   # 目标文件夹
    prefix   = "p0original_"                              # 要加在文件名前面的字符
    # ==================================
    add_prefix_to_files(dir_path, prefix)
