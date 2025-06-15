import os
import numpy as np
import nibabel as nib
import scipy.ndimage as ndi  # 形态学操作需要

# ---------- 0. 路径 ----------
input_image_dir = rf'F:\ADNI数据集902样本\06-PET配准_去头骨_平滑\01PET配准\MNI_1mm'
input_mask_dir  = rf'F:\ADNI数据集902样本\05-MRI头骨分离\p0original\01配准至MNI\1mm'
output_dir      = rf'F:\ADNI数据集902样本\06-PET配准_去头骨_平滑\02PET去头骨\MNI_1mm'
os.makedirs(output_dir, exist_ok=True)

# ---------- 1. 遍历 ----------
for image_fname in os.listdir(input_image_dir):
    if not image_fname.endswith('.nii'):
        continue

    # 1.1 读入原始 T1 / wm 图
    img_path = os.path.join(input_image_dir, image_fname)
    img_nii  = nib.load(img_path)
    img_data = img_nii.get_fdata()            # float64 by default

    # 1.2 构造对应的 mask 文件名
    mask_fname = 'p0' + image_fname.replace('原始图像', '蒙版序列')
    mask_path  = os.path.join(input_mask_dir, mask_fname)
    if not os.path.exists(mask_path):
        print(f'[WARN] Mask not found for: {image_fname}')
        continue

    # ---------- 2. 处理 mask ----------
    mask_data = nib.load(mask_path).get_fdata()
    mask_bool = mask_data > 0                 # p0 标签 1‒3 视为脑

    # 可选：开运算去毛刺 + 闭运算填孔 + 仅保最大连通域
    # mask_bool = ndi.binary_opening(mask_bool, iterations=1)
    # mask_bool = ndi.binary_closing(mask_bool, iterations=1)
    # labeled, _ = ndi.label(mask_bool)
    # largest = np.argmax(np.bincount(labeled.ravel())[1:]) + 1
    # mask_bool = labeled == largest

    # ---------- 3. 乘回原图 ----------
    out_data = img_data * mask_bool

    # ---------- 4. 强制写成 float32 ----------
    out_data = out_data.astype(np.float32)
    out_nii  = nib.Nifti1Image(out_data, affine=img_nii.affine, header=img_nii.header)
    out_nii.header.set_data_dtype(np.float32)  # 同步头信息

    # ---------- 5. 保存 ----------
    out_fname = image_fname.replace('.nii', '_brain.nii')
    nib.save(out_nii, os.path.join(output_dir, out_fname))
    print(f'[OK] Saved: {out_fname}')

print('全部处理完成！')
