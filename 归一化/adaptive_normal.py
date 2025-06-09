import os, glob, sys, locale
from pathlib import Path
import numpy as np
import SimpleITK as sitk

# ---- Windows 下强制 UTF-8，防乱码 ----
if sys.platform.startswith("win"):
    os.environ.setdefault("PYTHONUTF8", "1")
    try:
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    except locale.Error:
        pass


def adaptive_normal(image_path: str, outpath: str, eps: float = 1e-6) -> str:
    """
    Robust intensity normalisation to [-1, 1] using 0.1%–99.9% quantiles.
    NaN / ±Inf 会被视为背景 (-1)，避免污染分位统计。
    """
    # 读取影像并转 float32
    img = sitk.ReadImage(image_path)
    arr = sitk.GetArrayFromImage(img).astype(np.float32)

    # ① 将 NaN、Inf 映射为 -1（背景）
    arr[~np.isfinite(arr)] = -1.0

    # ② 前景体素（>0）
    fg = arr[arr > 0]
    if fg.size == 0:                               # 整幅全背景
        print(f"[WARN] All-zero image: {image_path}")
        sitk.WriteImage(img, outpath)
        return os.path.abspath(outpath)

    # ③ 0.1%–99.9% 分位
    lo, hi = np.percentile(fg, [0.1, 99.9])
    std = max((hi - lo) / 2.0, eps)               # 加 ε 防除 0
    mean = (hi + lo) / 2.0

    # ④ 归一化并截断到 [-1,1]
    arr = np.clip((arr - mean) / std, -1.0, 1.0)

    # ⑤ 写回 NIfTI，保持空间信息
    out_img = sitk.GetImageFromArray(arr)
    out_img.CopyInformation(img)
    sitk.WriteImage(out_img, outpath)
    return os.path.abspath(outpath)


def adaptive_normal_dir(in_dir: str, out_dir: str):
    """
    批量处理目录下所有 .nii / .nii.gz
    """
    os.makedirs(out_dir, exist_ok=True)
    nii_list = glob.glob(os.path.join(in_dir, "*.nii*"))

    for nii_path in nii_list:
        fname = Path(nii_path).name
        out_path = os.path.join(out_dir, fname)
        adaptive_normal(nii_path, out_path)
        print(f"Processed: {fname}  →  {out_path}")


# --------------------- 示例 ---------------------
if __name__ == "__main__":
    src = rf"E:\ADNI数据集902样本\05-mask处理后全脑图像\MRI_MNI_1mm"
    dst = rf"E:\ADNI数据集902样本\05-mask处理后全脑图像\MRI_MNI_1mm-normal"
    adaptive_normal_dir(src, dst)
