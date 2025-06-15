# ADNI 影像预处理-分析代码总览  
> 面向 **AD/MCI vs. NC** 研究的一整套 MRI-PET 预处理 + QC + 统计工作流  
> MATLAB-SPM 与 纯 Python/ITK 双栈并行，方便在 Windows-MATLAB 和 Linux-Docker 环境间切换。

---

## 1. 目录总览

├─mat_tools/ # MATLAB-SPM 批处理脚本

├─normalization/ # PET/MRI 强度归一化（Python）

├─py_tools/ # 通用 Python 影像处理脚本

├─skull_separation/ # PET 去颅骨（Python 单/批处理）

└─utils/ # 模板、字典、转换工具等


---

## 2. `mat_tools/` —— SPM 批量脚本

| 文件 | 作用 | 典型输入 → 输出 |
|------|------|----------------|
| `batch_coregister_mri.m` | **MRI → MNI 配准** | 原始 T1 → rT1 |
| `batch_coregister_pet.m` | **PET → MRI 配准**，包含normallization操作 | PET → wrPET |
| `batch_norm_MRI_only.m` | 仅对 MRI 做 SPM **Normalization** | T1 → wrT1 |
| `coregister_job.m` | 配准通用子函数，被 `batch_coregister_*` 调用 | — |
| `normalise_job.m` | SPM Normalise 的低层封装 | — |
| `PET_batch_skull_separation.m` | 调用 `imcalc`：`PET×(MRI>0)` 批量PET头骨分离 | wrPET + p0mask → skullfree_wrPET |
| `Smooth.m` | 高斯平滑（自定义FWHM平滑核） | skullfree_* → s6_skullfree_* |
| `PET_Intensity.m` | 统计 & 写入 PET 全局强度 | PET → `.csv` |
| `Fun_Split_4DTo3D.m` / `Main_Fun_Split_4DTo3D.m` | 将 4D fMRI/NIfTI 切为 3D | 4D → 多个 3D |
| `p0mask_all_to_mni.m` | 将 CAT12 `p0*` 掩膜批量变换到 MNI（自定义体素和分辨率大小） | p0mask → wp0mask |
| `Reorient.m` / `spm_auto_reorient.m` | 半自动对齐 AC-PC 线，修 header | 原始 → r* |
| `Reslice_ROI.m` | 将 atlas/ROI 重采样到被试空间 | ROI → Reslice_ROI |
| `err_*.log`, `*.ps` | 批处理错误、SPM 图形输出信息等 | — |

---

## 3. `skull_separation/` —— 去颅骨-快速处理 & float32精度（Python）

| 文件 | 说明 |
|------|------|
| `skull_separation-single.py` | 单例：`PET.nii` + `p0mask.nii` → `PET_brain.nii` |
| `skull_separation.py` | **批量版**，可指定输入/输出目录并多线程。|
| `QC.py` | 计算去骨前后体素分布、体积差、生成直方图。|

>与 `mat_tools/PET_batch_skull_separation.m` 区别：  
> - **Python** 版保持 `float32`，可接着做 NumPy/torch 运算，但是存储空间占用大；  
> - 不会自动重采样，PET 与掩膜需同空间，也就是先配准PET和MRI，再对PET去头骨；  
> - 可选 `binary_opening` / `largest_component` 做形态学清理（代码中有，默认不做）。


---

## 4. `normalization/` —— PET/MRI 强度归一化

| 文件 | 功能简述 |
|------|----------|
| `adaptive_normal.py` | **鲁棒线性归一化**：0.1%–99.9% 分位映射到 \[-1,1]，并自动把 NaN / ±Inf 当背景处理。|
| `check.py` | 逐例打印归一化前后最小值/最大值，生成 QC 表。|
| `size_check.py` | 快捷统计文件夹内所有 NIfTI 的维度 & 体素尺寸。|
| `nii_check_results.txt` | 上述检查脚本输出的汇总。|


---

## 5. `py_tools/` —— 通用 Python 工具箱

> 所有与 NIfTI/DICOM 操作、空间校准、重采样、数据 QC 以及文件命名相关的 **Python 脚本**。  
> **依赖**：Python 3.9+、Nibabel、SimpleITK、NumPy、Pandas、scikit-image 等（各脚本头部已注明）。

---

### （1）路径与文件管理

| 脚本 | 功能 |
|------|------|
| **`datapath_modif.py`** | 统一重写数据根目录（如换服务器后批量调整路径）。支持：<br>• JSON/YAML 配置批量替换<br>• 递归扫描 CSV/TSV & 更新列中路径 |
| **`search_4D.py`** | 在多层目录中寻找 4D NIfTI（维度 ≥ 4），输出列表或复制到指定文件夹 |
| **`rename-1.py`** | 批量重命名脚本，供其他脚本调处理后保存结果时调用。示例：`sub-IMG_001.nii → IMG_001.nii` |
| **`rename-2.py`** | 批量重命名脚本，供其他脚本调处理后保存结果时调用。示例：`IMG_001-smooth.nii → IMG-001.nii` |
| **`rename+1.py`** | 批量重命名脚本，供其他脚本调处理后保存结果时调用。示例：`IMG_001.nii → normal_IMG-001.nii` |

---

### （2）格式转换

| 脚本 | 作用 |
|------|------|
| **`dcm2nii_all.py`** | 批量调用 **dcm2niix** 将 DICOM 转 NIfTI，自动按受试者/时间点分目录保存 |
| **`nii2gz.py`** | `.nii -> .nii.gz` 批处理单文件转换，保持 header 不变 |
| **`niigz2nii.py`** | `.nii.gz -> .nii` 批处理单文件转换，保持 header 不变 |

---

### （3）图像尺寸 / 体素检查

| 脚本 | 功能 |
|------|------|
| **`get_size&voxel.py`** | 对文件夹内 NIfTI 逐一读取 **体素尺寸(spacing)** 与 **矩阵大小(shape)**，汇总成 CSV |
| **`checking_dim.py`** | 快速检测是否有维度不一致的异常文件；可设定允许误差（如 ±1 像素） |
| **`check_resample_image.py`** | 验证重采样前后 header：spacing、origin、direction 是否匹配；打印差异并生成报告 |

---

### （4）配准 / 重采样 / 预处理

| 脚本 | 说明 |
|------|------|
| **`register_pet2mri.py`** | **SimpleITK** 互信息配准：将 PET 刚性对齐到 MRI，输出变换矩阵 + 对齐后影像 |
| **`resample.py`** | 按 **目标 spacing** 重采样（线性 / 最近邻 / B-Spline 自选），指定图像大小和体素，可以用于去除背景黑边 |
| **`resize.py`** | 按 **目标 体素**（如 1mm、1.5mm）重采样；自动调整图像的大小 |
| **`N4_Bias_correction.py`** | ITK 实现的 **N4 偏场校正**：去除 MRI 低频非均匀性 |
| **`ac_pc.py`** | 利用 Otsu + 中线投影，估算 AC-PC 点并改写 affine，使大脑水平。适合在无 MATLAB 环境下快速 Reorient |

---

### （5）质量控制（QC）

| 脚本 | 描述 |
|------|------|
| **`PET_Intensity.py`** | 统计 PET 全局平均 SUV 或总 counts，并写入 `PET_DATA.csv` |
| **`qc_pet_mri.py`** | 生成 PET-MRI 叠加 PNG、计算互信息/SSIM，直观检查配准效果 |
| **`QC_Check.py`** | 综合 QC：<br>1. 读取多项指标（尺寸、spacing、强度范围、掩膜体积）<br>2. 规则判定 PASS/FAIL<br>3. 输出彩色 HTML 报告 |

---

## 6. `utils/` —— 模板、字典、转换工具等

| 类别 | 典型文件 | 说明 |
|------|----------|------|
| 模板 & Atlas | `mni_icbm152_...nii`、`aal3.nii`、`Reslice_aal3.nii` | MNI 标准脑、AAL3 对应不同分辨率 |
| 字典 | `.csv`| 大脑模板、大脑图谱的字典说明文件 |
| 转换工具 | `dcm2niix.exe` | DICOM→NIfTI 转换工具 |


---

## 7. 注意事项
---

**虚拟环境**：建议为 Python 工具单独建 Conda 环境 `conda env create -f env_mri.yml`，避免系统包冲突。  

**推荐工作链**

1. **DICOM→NIfTI** (`dcm2niix.exe` / `dcm2nii_all.py`)  
2. **初步 Reorient** (`spm_auto_reorient.m` → `Reorient.m`)  
3. **MRI → MNI / PET → MRI 输出 wr*** (`batch_coregister_*`, `batch_norm_MRI_only.m`)  
4. **CAT12 分割** 生成 `p0*` (脑掩膜)、`y*` (到MNI空间变形场)  
5. **MRI&PET 去颅骨** 任选  
   - SPM ：`PET_batch_skull_separation.m`  
   - Python ：`skull_separation.py`   
6. **平滑** PET: `PET_Smooth.m` (6 mm)；MRI: 自行选 2 mm/4 mm  
7. **强度归一化 & 调整大小** `adaptive_normal.py` → `resize.py` 
8. **质量控制** `QC.py`, `QC_Check.py`, `qc_pet_mri.py` 

---

## 8. FAQ

- **MATLAB vs. Python 结果能混用吗？**  
  可以，只要确保空间对齐和数据类型一致。Python 阶段可读 `.nii`/`.nii.gz` 任意格式。  

- **为什么同时保留两套脚本？**  
  - SPM 对 **空间变换** 更稳健，批量脚本方便可视化。  
  - Python 在 **形态学清洗 / GPU 推理** 更灵活，服务器无需 MATLAB 许可。  

- **如何确定脚本运行顺序？**  
  见“推荐完整工作链”，亦可按自身实验设计增删步骤。  

---

