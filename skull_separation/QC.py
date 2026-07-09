import os, glob, nibabel as nib, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import zscore

DATA_DIR   = rf'C:\Users\dongz\Desktop\mask\mri'
IMAGE_PAT  = 'p0_*'
THRESHOLDS = [0.0]            # p0 only needs one threshold: >0.
rows = []

for f in glob.glob(os.path.join(DATA_DIR, IMAGE_PAT)):
    subj = os.path.basename(f).split('_')[1]      # Adjust this according to the filename format.
    data = nib.load(f).get_fdata()
    # >0 mask.
    voxels = np.count_nonzero(data > 1e-6)
    rows.append((subj, 0, voxels))

df = pd.DataFrame(rows, columns=['Subject', 'Threshold', 'Brain_Voxels'])

# ------- z-score: compute only when there is more than one subject. -------
if df['Subject'].nunique() > 1:
    df['Z'] = df.groupby('Threshold')['Brain_Voxels']\
                .transform(lambda x: zscore(x, ddof=1))
    df['Outlier'] = df['Z'].abs() > 3
else:
    df['Z'] = 0
    df['Outlier'] = False

df.to_csv('qc_p0_gt0.csv', index=False)
print(df.head())
