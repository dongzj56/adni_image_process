'''用于重命名目录下所有文件的脚本
去除文件名前缀'''
import os
import shutil

# 从用户输入获取目录路径
directory = input("请输入目录路径: ")
# 去除可能的引号
directory = directory.strip('"').strip("'")

# 获取要去除的字符长度
try:
    remove_length = int(input("请输入要从文件名前面去除的字符长度: "))
    if remove_length < 0:
        print("字符长度必须为正整数，将使用默认值0")
        remove_length = 0
except ValueError:
    print("输入无效，将使用默认值0")
    remove_length = 0

# 确保目录存在
if not os.path.exists(directory):
    print(f"目录 {directory} 不存在！")
else:
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 获取完整的文件路径
        file_path = os.path.join(directory, filename)
        
        # 检查是否为文件（而非目录）
        if os.path.isfile(file_path):
            # 如果文件名长度大于要去除的长度，则去掉前面的字符
            if len(filename) > remove_length:
                new_filename = filename[remove_length:]
                new_file_path = os.path.join(directory, new_filename)
                
                # 重命名文件
                try:
                    shutil.move(file_path, new_file_path)
                    print(f"已重命名: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"重命名 {filename} 时出错: {e}")
            else:
                print(f"跳过 {filename}，因为文件名长度不足")
    
    print("重命名操作完成！")