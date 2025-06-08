%------------------------------------------------------------------
% batch_MNI_write.m  ── 批量将 NIfTI 写入 MNI 空间 (2 mm³)
% 依赖：SPM12 已安装并在 MATLAB 路径内
%------------------------------------------------------------------

clear; clc;

%% 1. 指定目录
img_dir = 'F:\ADNI数据集902样本\05-mask处理后全脑图像\MRI_170_256_256';
def_dir = 'F:\ADNI数据集902样本\04-MRI头骨分离结果\MRI\ADNI\mri';

%% 2. 收集影像列表（过滤掉 y_ / w_ 等已处理文件）
img_struct = dir(fullfile(img_dir, '*.nii'));                  % 只处理 .nii
names      = {img_struct.name};
keep_mask  = ~startsWith(names, {'y_', 'w_', 'm', 'c', 'o'});  % 可按需调整过滤规则
img_struct = img_struct(keep_mask);

%% 3. 构建 matlabbatch
matlabbatch = {};   % 动态扩展
skip_count  = 0;

for i = 1:numel(img_struct)
    img_name = img_struct(i).name;
    def_name = ['y_' img_name];                                % 匹配位移场
    def_path = fullfile(def_dir, def_name);
    img_path = fullfile(img_dir, img_name);

    if ~isfile(def_path)
        fprintf(2, '× 缺少位移场，跳过：%s\n', img_name);
        skip_count = skip_count + 1;
        continue;
    end

    k = numel(matlabbatch) + 1;                                % 下一个 batch 单元
    matlabbatch{k}.spm.spatial.normalise.write.subj.def      = {def_path};
    matlabbatch{k}.spm.spatial.normalise.write.subj.resample = {[img_path ',1']};

    % 写入参数（保持与之前一致，可自行修改）
    matlabbatch{k}.spm.spatial.normalise.write.woptions.bb     = [-90 -126 -72; 90 90 108];
    matlabbatch{k}.spm.spatial.normalise.write.woptions.vox    = [1 1 1];
    matlabbatch{k}.spm.spatial.normalise.write.woptions.interp = 4;
    matlabbatch{k}.spm.spatial.normalise.write.woptions.prefix = 'w';
end

fprintf('\n共发现 %d 例影像，成功匹配 %d 例，缺失 %d 例位移场。\n', ...
        numel(img_struct)+skip_count, numel(matlabbatch), skip_count);

if isempty(matlabbatch)
    error('未找到可处理的配对文件，脚本终止。');
end

%% 4. 运行 SPM 批处理
spm('defaults', 'FMRI');
spm_jobman('run', matlabbatch);

fprintf('\n✓ 全部已写入 MNI 空间（输出前缀 "w"）\n');
