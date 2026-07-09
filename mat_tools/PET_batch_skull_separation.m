% PET_skull_separation_batch.m
% Batch skull-strip PET (wr*) images using the corresponding MRI mask (wm*).
% Dependency: SPM12.

%% 0. Configuration.
petDir = 'F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\01PET_registered\MNI_2mm';         % PET image folder (wr prefix).
mriDir = 'F:\ADNI_dataset_902_samples\05-MRI_skull_stripping\p0original\01registered_to_MNI\2mm';         % MRI mask folder (wm prefix).
outDir = 'F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\02PET_skull_stripped\MNI_2mm';  % Output directory after skull stripping.

if ~exist(outDir,'dir')
    mkdir(outDir);
end

%% 1. Initialize the SPM PET environment.
spm('defaults','PET');
spm_jobman('initcfg');

%% 2. Scan all PET files (wr*.nii).
petList = dir(fullfile(petDir,'wr*.nii'));

for i = 1:numel(petList)
    petName = petList(i).name;
    [~, baseName] = fileparts(petName);
    
    % Extract subject ID.
    % wr002_S_2043.nii -> subjID = '002_S_2043'
    subjID = baseName(3:end);
    
    % Match the wm mask file in the MRI folder.
    maskName = ['p0' subjID '.nii'];
    wmPath   = fullfile(mriDir, maskName);
    if ~exist(wmPath, 'file')
        warning('Mask file %s not found, skipped %s', maskName, petName);
        continue;
    end
    
    %% 3. Build the SPM batch.
    matlabbatch = {};
    matlabbatch{1}.spm.util.imcalc.input = {
        [wmPath      ',1']   % i1: MRI mask.
        [fullfile(petDir, petName) ',1']   % i2: PET image.
    };
    matlabbatch{1}.spm.util.imcalc.output  = ['skullfree_' baseName];
    matlabbatch{1}.spm.util.imcalc.outdir  = { outDir };
    % Core expression: multiply the PET image by the mask region (wm > 0).
    matlabbatch{1}.spm.util.imcalc.expression = 'i2.*(i1>0)';
    matlabbatch{1}.spm.util.imcalc.var        = struct('name', {}, 'value', {});
    matlabbatch{1}.spm.util.imcalc.options.dmtx   = 0;
    matlabbatch{1}.spm.util.imcalc.options.mask   = 0;
    matlabbatch{1}.spm.util.imcalc.options.interp = 1;
    matlabbatch{1}.spm.util.imcalc.options.dtype  = 4;
    
    %% 4. Run and report.
    spm_jobman('run', matlabbatch);
    fprintf('Skull stripping complete for %s. Result: %s\\skullfree_%s.nii\n', ...
        petName, outDir, baseName);
end

fprintf('All PET skull-stripping processing is complete. Scanned %d wr* files.\n', numel(petList));
