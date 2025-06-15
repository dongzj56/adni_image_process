% PET_smooth_batch.m
% 一键批量对 PET 影像做高斯平滑，结果保存到新的文件夹下
% 依赖：SPM12

%% 0. —— 配置区 —— 
petDir = 'F:\ADNI数据集902样本\06-PET配准_去头骨_平滑\02PET去头骨\MNI_1mm';      % 放原始 PET .nii 的文件夹
outDir = 'F:\ADNI数据集902样本\06-PET配准_去头骨_平滑\03PET平滑4mm\MNI_1mm'; % 平滑结果输出目录

% 如果输出目录不存在，就新建

if ~exist(outDir,'dir')
    mkdir(outDir);
end

%% 1. 初始化 SPM PET 环境
spm('defaults','fmri');
spm_jobman('initcfg');

%% 2. 扫描 PET 文件夹下所有 .nii
petList = dir(fullfile(petDir,'*.nii'));  % 扫描所有 PET 图像 :contentReference[oaicite:1]{index=1}

for i = 1:numel(petList)
    petName = petList(i).name;
    petPath = fullfile(petDir, petName);
    
    %% 3. 构建平滑批处理
    matlabbatch = {};
    matlabbatch{1}.spm.spatial.smooth.data   = { [petPath ',1'] };
    matlabbatch{1}.spm.spatial.smooth.fwhm   = [4 4 4];     % 高斯核大小 :contentReference[oaicite:2]{index=2}
    matlabbatch{1}.spm.spatial.smooth.dtype  = 0;
    matlabbatch{1}.spm.spatial.smooth.im     = 0;
    matlabbatch{1}.spm.spatial.smooth.prefix = 'smooth_';
    
    %% 4. 运行 SPM 批处理
    spm_jobman('run', matlabbatch);
    fprintf('✓ 已平滑 %s\n', petName);
    
    %% 5. 移动结果到输出目录
    origSmooth = fullfile(petDir, ['smooth_' petName]);
    newSmooth  = fullfile(outDir, ['smooth_' petName]);
    if exist(origSmooth,'file')
        movefile(origSmooth, newSmooth);
    else
        warning('未找到平滑结果：%s', origSmooth);
    end
end

fprintf('全部完成：共处理 %d 个文件，结果保存在 %s\n', numel(petList), outDir);
