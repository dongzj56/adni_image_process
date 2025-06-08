% ① 影像所在文件夹（193×229×193 或其它尺寸）
MRI_DIR = 'F:\ADNI数据集902样本\05-mask处理后全脑图像\MRI_MNI_193_229_193';

% ② 同一批被试的变形场存放处
DEF_DIR = 'F:\ADNI数据集902样本\04-MRI头骨分离结果\MRI\ADNI\mri';

batch_reslice_mri_job(MRI_DIR, DEF_DIR, 'wr', 0, 4);     % 会产生 wr*.nii

function batch_reslice_mri_job(MRI_DIR, DEF_DIR, outputPrefix, verbose, interp)
% 仅利用现成 y_*.nii，把 MRI 重采样到 MNI (113×137×113, 1.5 mm³)
% -------------------------------------------------------------------------
% MRI_DIR      待重采样的 T1 图像所在目录 (*.nii)
% DEF_DIR      与之匹配的 y_*.nii 目录，可与 MRI_DIR 不同
% outputPrefix 写入 MNI 的文件前缀，默认 'wr'
% verbose      0/1：SPM 详细输出，默认 0
% interp       0–7：插值方式，默认 4 (cubic)
%
% 依赖：normalise_job.m   —— 控制 bb / vox / 前缀
% -------------------------------------------------------------------------

if nargin < 3 || isempty(outputPrefix), outputPrefix = 'wr'; end
if nargin < 4 || isempty(verbose),      verbose = 0;        end
if nargin < 5 || isempty(interp),       interp  = 4;        end

spm('Defaults','fMRI');  spm_jobman('initcfg');

fid = fopen('err_mri_reslice.log','w+');      % 记录缺失或错误
if fid == -1, error('无法写入日志文件'); end

allMRI = dir(fullfile(MRI_DIR,'*.nii'));
done   = startsWith({allMRI.name}, outputPrefix);
TODO   = allMRI(~done);

fprintf('Total MRI: %d | Pending: %d\n', numel(allMRI), numel(TODO));

for k = 1:numel(TODO)
    mriFile   = TODO(k).name;
    srcPath   = fullfile(MRI_DIR, mriFile);

    % ---- 根据文件名在 DEF_DIR 寻找匹配的 y_*.nii ----
    % 先把 wr / r / m 等前缀剥掉，得到“裸文件名”
    [~, baseName, ~] = fileparts(mriFile);
    baseName = regexprep(baseName, '^[a-z]+', '');   % 去掉前缀字母串
    cand = dir(fullfile(DEF_DIR, ['y_*', baseName, '*.nii']));
    if isempty(cand)
        fprintf(fid, '[Missing y_] %s\n', mriFile);
        warning('[Missing y_] %s，已跳过', mriFile);
        continue;
    end
    defPath = fullfile(DEF_DIR, cand(1).name);       % 取第一个匹配

    fprintf('[%3d/%3d] %s  ←  %s\n', k, numel(TODO), mriFile, cand(1).name);

    try
        % 调用你的工具函数，真正完成写入 (113×137×113, 1.5 mm³)
        normalise_job(defPath, srcPath, interp, outputPrefix, verbose);
    catch ME
        fprintf(fid, '[Normalise Error] %s: %s\n', mriFile, ME.message);
        warning('[Normalise Error] %s，已记录', mriFile);
    end
end

fclose(fid);
fprintf('\n✓ 全部处理完毕！结果文件前缀 “%s”\n', outputPrefix);
end
