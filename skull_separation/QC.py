import os, glob, nibabel as nib, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import zscore

DATA_DIR   = rf'C:\Users\dongz\Desktop\mask\mri'
IMAGE_PAT  = 'p0_*'
THRESHOLDS = [0.0]            # p0 只需要一个阈值：>0
rows = []

for f in glob.glob(os.path.join(DATA_DIR, IMAGE_PAT)):
    subj = os.path.basename(f).split('_')[1]      # 自己根据文件名格式调整
    data = nib.load(f).get_fdata()
    # >0 掩膜
    voxels = np.count_nonzero(data > 1e-6)
    rows.append((subj, 0, voxels))

df = pd.DataFrame(rows, columns=['Subject', 'Threshold', 'Brain_Voxels'])

# ------- z-score：多于 1 个被试才计算 -------
if df['Subject'].nunique() > 1:
    df['Z'] = df.groupby('Threshold')['Brain_Voxels']\
                .transform(lambda x: zscore(x, ddof=1))
    df['Outlier'] = df['Z'].abs() > 3
else:
    df['Z'] = 0
    df['Outlier'] = False

df.to_csv('qc_p0_gt0.csv', index=False)
print(df.head())
