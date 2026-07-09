% PET_smooth_batch.m
% Batch-apply Gaussian smoothing to PET images and save results to a new folder.
% Dependency: SPM12.

%% 0. Configuration.
petDir = 'F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\02PET_skull_stripped\MNI_1mm';      % Folder containing original PET .nii files.
outDir = 'F:\ADNI_dataset_902_samples\06-PET_registration_skull_stripping_smoothing\03PET_smoothing4mm\MNI_1mm'; % Output directory for smoothed results.

% Create the output directory if it does not exist.

if ~exist(outDir,'dir')
    mkdir(outDir);
end

%% 1. Initialize the SPM PET environment.
spm('defaults','fmri');
spm_jobman('initcfg');

%% 2. Scan all .nii files in the PET folder.
petList = dir(fullfile(petDir,'*.nii'));  % Scan all PET images.

for i = 1:numel(petList)
    petName = petList(i).name;
    petPath = fullfile(petDir, petName);
    
    %% 3. Build the smoothing batch.
    matlabbatch = {};
    matlabbatch{1}.spm.spatial.smooth.data   = { [petPath ',1'] };
    matlabbatch{1}.spm.spatial.smooth.fwhm   = [4 4 4];     % Gaussian kernel size.
    matlabbatch{1}.spm.spatial.smooth.dtype  = 0;
    matlabbatch{1}.spm.spatial.smooth.im     = 0;
    matlabbatch{1}.spm.spatial.smooth.prefix = 'smooth_';
    
    %% 4. Run SPM batch processing.
    spm_jobman('run', matlabbatch);
    fprintf('Smoothed %s\n', petName);
    
    %% 5. Move the result to the output directory.
    origSmooth = fullfile(petDir, ['smooth_' petName]);
    newSmooth  = fullfile(outDir, ['smooth_' petName]);
    if exist(origSmooth,'file')
        movefile(origSmooth, newSmooth);
    else
        warning('Smoothed result not found: %s', origSmooth);
    end
end

fprintf('All done: processed %d files. Results saved in %s\n', numel(petList), outDir);
