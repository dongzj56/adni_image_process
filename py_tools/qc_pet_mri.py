
"""
qc_pet_mri.py
--------------
自动批量质量检测脚本，评估配准后的 MRI (wT1) 与 PET (wrPET) 是否对齐。

依赖：
    pip install nibabel numpy scipy pandas

用法示例：
    python qc_pet_mri.py --mri_dir /path/to/MRI --pet_dir /path/to/PET \
                         --mri_prefix w --pet_prefix wr \
                         --dice_th 0.75 --dist_th 5 --mi_bins 64

输出：
    1. qc_metrics.csv   —— 每个受试者的 Dice、重心距离、互信息、是否fail
    2. 在终端打印失配病例列表
"""

import argparse
import nibabel as nib
import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
from pathlib import Path

def dice_coef(mask1: np.ndarray, mask2: np.ndarray) -> float:
    intersection = np.logical_and(mask1, mask2).sum()
    return 2.0 * intersection / (mask1.sum() + mask2.sum() + 1e-8)

def centroid(mask: np.ndarray):
    coords = np.column_stack(np.nonzero(mask))
    return coords.mean(axis=0)

def mutual_information(a, b, bins=64):
    # flatten masks
    a = a.ravel()
    b = b.ravel()
    hist_2d, _, _ = np.histogram2d(a, b, bins=bins)
    p_xy = hist_2d / hist_2d.sum()
    p_x = p_xy.sum(axis=1)
    p_y = p_xy.sum(axis=0)
    nz = p_xy > 0
    return (p_xy[nz] * (np.log(p_xy[nz]) - np.log(p_x[:, None][nz]) - np.log(p_y[None, :][nz]))).sum()

def simple_pet_mask(pet):
    return pet > 0.05 * pet.max()

def simple_mri_mask(mri):
    return mri > 0  # assume skull‑stripped or non‑zero voxels are brain

def parse_args():
    parser = argparse.ArgumentParser(description='QC PET/MRI registration')
    parser.add_argument('--mri_dir', required=True, help='Dir with wT1 MRI NIfTI')
    parser.add_argument('--pet_dir', required=True, help='Dir with wrPET NIfTI')
    parser.add_argument('--mri_prefix', default='w', help='Prefix of processed MRI files')
    parser.add_argument('--pet_prefix', default='wr', help='Prefix of processed PET files')
    parser.add_argument('--dice_th', type=float, default=0.75, help='Dice threshold to flag failure')
    parser.add_argument('--dist_th', type=float, default=5.0, help='Centroid distance (mm) threshold')
    parser.add_argument('--mi_bins', type=int, default=64, help='Bins for mutual information')
    return parser.parse_args()

def main():
    args = parse_args()
    mri_files = {f.name.replace(args.mri_prefix,'').split('.')[0]: f for f in Path(args.mri_dir).glob(f'{args.mri_prefix}*.nii*')}
    pet_files = {f.name.replace(args.pet_prefix,'').split('.')[0]: f for f in Path(args.pet_dir).glob(f'{args.pet_prefix}*.nii*')}

    rows = []
    for sid, pet_path in pet_files.items():
        if sid not in mri_files:
            print(f'[WARN] MRI for subject {sid} not found, skip.')
            continue
        mri_path = mri_files[sid]
        mri = nib.load(mri_path).get_fdata()
        pet = nib.load(pet_path).get_fdata()

        m_mask = simple_mri_mask(mri)
        p_mask = simple_pet_mask(pet)

        dice = dice_coef(m_mask, p_mask)
        dist = euclidean(centroid(m_mask), centroid(p_mask))
        mi   = mutual_information(mri[m_mask], pet[m_mask], bins=args.mi_bins)

        fail = (dice < args.dice_th) or (dist > args.dist_th)

        rows.append(dict(subject=sid, dice=dice, centroid_mm=dist, mi=mi, failed=fail))

    df = pd.DataFrame(rows).sort_values('subject')
    df.to_csv('qc_metrics.csv', index=False)
    bad = df[df['failed']]
    print(f'QC completed: {len(df)} subjects, {len(bad)} flagged as FAIL')
    if not bad.empty:
        print('Failed subjects:')
        print(bad[['subject','dice','centroid_mm','mi']])

if __name__ == '__main__':
    main()
