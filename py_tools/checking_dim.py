import nibabel as nib
import os
import glob

def check_nifti_dimensions(directory):
    """
    检查指定目录下所有NIfTI文件的维度信息
    """
    # 获取所有.nii和.nii.gz文件
    file_list = glob.glob(os.path.join(directory, "*.nii")) + \
                glob.glob(os.path.join(directory, "*.nii.gz"))

    if not file_list:
        print("未找到任何NIfTI文件")
        return

    dimension_records = {}
    problem_files = []

    print("开始检查NIfTI文件维度...\n")
    
    for file_path in file_list:
        try:
            # 加载NIfTI文件
            img = nib.load(file_path)
            dim = img.header['dim'][1:5]  # 获取前4个维度（通常包括3D空间+时间维度）
            dim = tuple(map(int, dim))    # 转换为整数元组
            
            # 记录维度信息
            if dim not in dimension_records:
                dimension_records[dim] = []
            dimension_records[dim].append(os.path.basename(file_path))
            
            print(f"文件: {os.path.basename(file_path):<30} 维度: {dim}")
            
        except Exception as e:
            problem_files.append((file_path, str(e)))
            print(f"无法读取文件: {os.path.basename(file_path)} - 错误: {str(e)}")

    # 输出汇总报告
    print("\n==== 维度汇总 ====")
    for idx, (dim, files) in enumerate(dimension_records.items(), 1):
        print(f"{idx}. 维度 {dim}: {len(files)} 个文件")
        print("   示例文件: " + ", ".join(files[:3]) + ("..." if len(files)>3 else ""))

    # 显示问题文件
    if problem_files:
        print("\n==== 问题文件 ====")
        for idx, (path, err) in enumerate(problem_files, 1):
            print(f"{idx}. {os.path.basename(path)} - 错误: {err}")

if __name__ == "__main__":
    target_dir = input("请输入要检查的目录路径：").strip()
    
    if not os.path.isdir(target_dir):
        print("错误：指定的路径不存在或不是目录")
    else:
        check_nifti_dimensions(target_dir)