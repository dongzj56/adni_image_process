% PET_skull_separation_batch.m
% 一键批量对 PET（wr*）影像做头骨去除（基于对应 MRI 掩膜 wm*）
% 依赖：SPM12

%% 0. —— 配置区 —— 
petDir = 'F:\ADNI数据集902样本\03-ACPC校正\pet\ADNI';         % PET 影像文件夹（前缀 wr）
mriDir = 'F:\ADNI数据集902样本\04-MRI头骨分离结果\MRI\ADNI\mri';         % MRI 掩膜文件夹（前缀 wm）
outDir = 'F:\ADNI数据集902样本\06-PET配准_去头骨_平滑\02PET去头骨';  % 去骨后结果输出目录

if ~exist(outDir,'dir')
    mkdir(outDir);
end

%% 1. 初始化 SPM PET 环境
spm('defaults','PET');
spm_jobman('initcfg');

%% 2. 扫描所有 PET 文件（wr*.nii）
petList = dir(fullfile(petDir,'wr*.nii'));

for i = 1:numel(petList)
    petName = petList(i).name;
    [~, baseName] = fileparts(petName);
    
    % —— 提取受试者 ID —— 
    % wr002_S_2043.nii -> subjID = '002_S_2043'
    subjID = baseName(3:end);
    
    % —— 在 MRI 文件夹里匹配掩膜 wm 文件 —— 
    maskName = ['wm' subjID '.nii'];
    wmPath   = fullfile(mriDir, maskName);
    if ~exist(wmPath, 'file')
        warning('未找到掩膜文件 %s，跳过 %s', maskName, petName);
        continue;
    end
    
    %% 3. 构建 SPM 批处理
    matlabbatch = {};
    matlabbatch{1}.spm.util.imcalc.input = {
        [wmPath      ',1']   % i1: MRI 掩膜
        [fullfile(petDir, petName) ',1']   % i2: PET 图像
    };
    matlabbatch{1}.spm.util.imcalc.output  = ['skullfree_' baseName];
    matlabbatch{1}.spm.util.imcalc.outdir  = { outDir };
    % 核心表达式：PET 图像乘以掩膜（wm>0）区域 :contentReference[oaicite:0]{index=0}
    matlabbatch{1}.spm.util.imcalc.expression = 'i2.*(i1>0)';
    matlabbatch{1}.spm.util.imcalc.var        = struct('name', {}, 'value', {});
    matlabbatch{1}.spm.util.imcalc.options.dmtx   = 0;
    matlabbatch{1}.spm.util.imcalc.options.mask   = 0;
    matlabbatch{1}.spm.util.imcalc.options.interp = 1;
    matlabbatch{1}.spm.util.imcalc.options.dtype  = 4;
    
    %% 4. 运行并报告
    spm_jobman('run', matlabbatch);
    fprintf('✓ 已完成 %s 的头骨去除，结果：%s\\skullfree_%s.nii\n', ...
        petName, outDir, baseName);
end

fprintf('所有 PET 头骨去除处理完毕，共扫描 %d 个 wr* 文件。\n', numel(petList));
