import os
import nibabel as nib
import numpy as np

def crop_last_slices(input_nii_path, output_nii_path):
    """
    将 (113, 137, 113) 图像裁剪为 (112, 136, 112)，去掉
    X=112、Y=136、Z=112 三张最末切片。
    """
    img    = nib.load(input_nii_path)
    data   = img.get_fdata()
    affine = img.affine
    header = img.header.copy()

    if data.shape != (113, 137, 113):
        raise ValueError(f"{os.path.basename(input_nii_path)} 尺寸 {data.shape} ≠ (113,137,113)")

    cropped = data[:112, :136, :112]           # 112×136×112
    nib.save(nib.Nifti1Image(cropped, affine, header), output_nii_path)


def batch_crop_directory(input_dir, output_dir):
    """
    遍历 input_dir 中全部 .nii / .nii.gz 文件，批量裁剪并保存到 output_dir。
    生成文件名规则：原名 + '_crop'（扩展名保持不变）
    """
    if not os.path.isdir(input_dir):
        raise ValueError(f"输入目录不存在：{input_dir}")
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(input_dir):
        if not (fname.endswith('.nii') or fname.endswith('.nii.gz')):
            continue                                # 跳过非 NIfTI 文件
        in_path  = os.path.join(input_dir, fname)
        name, ext = os.path.splitext(fname)
        if ext == '.gz':           # 处理 .nii.gz 双扩展
            name, _ext2 = os.path.splitext(name)
            ext = '.nii.gz'
        out_fname = f"{name}_crop{ext}"
        out_path  = os.path.join(output_dir, out_fname)

        try:
            print(f"裁剪 {fname} → {out_fname} ...", end="")
            crop_last_slices(in_path, out_path)
            print(" ✅")
        except Exception as e:
            print(f" ❌ 失败：{e}")


if __name__ == "__main__":
    # 修改为你的输入和输出文件夹
    INPUT_DIR  = rf"C:\Users\dongz\Desktop\adni_dataset\PET_113_137_113"               # 裁剪前的 NIfTI 文件夹
    OUTPUT_DIR = rf"C:\Users\dongz\Desktop\adni_dataset\PET_113_137_113-1"       # 裁剪后文件保存到此文件夹

    batch_crop_directory(INPUT_DIR, OUTPUT_DIR)
    print("全部处理完成。")
