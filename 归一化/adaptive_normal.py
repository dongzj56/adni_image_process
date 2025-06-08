import os
import glob
import numpy as np
import SimpleITK as sitk
import os, sys, locale, glob
from pathlib import Path
import numpy as np
import SimpleITK as sitk

# ---- 让当前 Python 进程进入 UTF-8 模式（Windows 专用） ----
if sys.platform.startswith('win'):
    os.environ.setdefault('PYTHONUTF8', '1')   # PEP 540/686
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # or zh_CN.UTF-8
    except locale.Error:
        pass


def adaptive_normal(image_path, outpath):
    """
    Normalize image intensity to [-1, 1] using robust min-max (0.1%–99.9% quantiles),
    excluding background voxels (value < 0).

    Parameters
    ----------
    image_path : str
        Path to a .nii file (also works for .nii.gz)
    outpath : str
        Output filename (.nii) after normalization.

    Returns
    -------
    str
        Absolute path of the saved normalized image.
    """
    min_p = 0.001
    max_p = 0.999  # quantile prefer 98~99

    image = sitk.ReadImage(image_path)
    image_array = sitk.GetArrayFromImage(image)
    imgArray = np.float32(image_array)

    imgPixel = imgArray[imgArray >= 0]
    imgPixel.sort()

    index = int(round(len(imgPixel) - 1) * min_p + 0.5)
    index = max(0, min(index, len(imgPixel) - 1))
    value_min = imgPixel[index]

    index = int(round(len(imgPixel) - 1) * max_p + 0.5)
    index = max(0, min(index, len(imgPixel) - 1))
    value_max = imgPixel[index]

    mean = (value_max + value_min) / 2.0
    stddev = (value_max - value_min) / 2.0

    imgArray = (imgArray - mean) / stddev
    imgArray[imgArray < -1] = -1.0
    imgArray[imgArray > 1] = 1.0

    img = sitk.GetImageFromArray(imgArray, isVector=False)
    img.CopyInformation(image)                       # 保留原空间信息
    sitk.WriteImage(img, outpath)
    return os.path.abspath(outpath)


def adaptive_normal_dir(in_dir, out_dir):
    """
    Batch-process all .nii files in a directory with `adaptive_normal`.

    Parameters
    ----------
    in_dir : str
        Directory containing .nii files to be normalized.
    out_dir : str
        Directory to save the normalized .nii files (will be created if absent).
    """
    os.makedirs(out_dir, exist_ok=True)
    nii_list = glob.glob(os.path.join(in_dir, '*.nii'))

    for nii_path in nii_list:
        fname = os.path.basename(nii_path)
        out_path = os.path.join(out_dir, fname)
        adaptive_normal(nii_path, out_path)
        print(f'Processed: {fname} → {out_path}')


# 示例用法
if __name__ == '__main__':
    # 单文件
    # adaptive_normal('example.nii', 'example_norm.nii')

    # 目录批处理
    adaptive_normal_dir(rf'F:\ADNI数据集902样本\05-mask处理后全脑图像\MRI_MNI_1.5mm', rf'F:\ADNI数据集902样本\05-mask处理后全脑图像\MRI_MNI_1.5mm-normal')
