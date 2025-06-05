import nibabel as nib
import numpy as np

def check_last_slices_are_background(nifti_path, background_value=0):
    """
    检查 NIfTI 图像在三个维度上的最后一行（即最末端切片）是否全为背景值（默认 0）。

    参数：
    - nifti_path:     输入 NIfTI 文件路径，假设其尺寸为 (113, 137, 113)。
    - background_value: 背景体素的值，通常为 0。

    返回：
    一个字典，包含以下布尔值：
      - 'x_slice_all_bg': 在 X 轴索引为 112 的切片是否全为背景。
      - 'y_slice_all_bg': 在 Y 轴索引为 136 的切片是否全为背景。
      - 'z_slice_all_bg': 在 Z 轴索引为 112 的切片是否全为背景。
    """
    img = nib.load(nifti_path)
    data = img.get_fdata()

    # 确认原始尺寸为 (113, 137, 113)
    if data.shape != (113, 137, 113):
        raise ValueError(f"图像尺寸为 {data.shape}，而不是预期的 (113, 137, 113)。")

    # X 方向最后一行：索引 112
    x_idx = data.shape[0] - 1  # 112
    x_slice = data[x_idx, :, :]

    # Y 方向最后一行：索引 136
    y_idx = data.shape[1] - 1  # 136
    y_slice = data[:, y_idx, :]

    # Z 方向最后一行：索引 112
    z_idx = data.shape[2] - 1  # 112
    z_slice = data[:, :, z_idx]

    results = {
        'x_slice_all_bg': np.all(x_slice == background_value),
        'y_slice_all_bg': np.all(y_slice == background_value),
        'z_slice_all_bg': np.all(z_slice == background_value),
    }
    return results


if __name__ == "__main__":
    # 示例：将下面路径改成你的 NIfTI 文件路径
    nifti_file = rf"GM\002_S_2043.nii"
    check_result = check_last_slices_are_background(nifti_file)

    print("检查结果：")
    print(f"X 方向索引 112 的切片全为背景吗？ {'是' if check_result['x_slice_all_bg'] else '否'}")
    print(f"Y 方向索引 136 的切片全为背景吗？ {'是' if check_result['y_slice_all_bg'] else '否'}")
    print(f"Z 方向索引 112 的切片全为背景吗？ {'是' if check_result['z_slice_all_bg'] else '否'}")
