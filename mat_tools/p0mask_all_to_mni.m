%------------------------------------------------------------------
% batch_MNI_write.m -- batch-write NIfTI images to MNI space (2 mm3).
% Dependency: SPM12 must be installed and available on the MATLAB path.
%------------------------------------------------------------------

clear; clc;

%% 1. Specify directories.
img_dir = 'E:\ADNI_dataset_902_samples\05-MRI_skull_stripping\WM';
def_dir = 'E:\ADNI_dataset_902_samples\04-MRI-CAT12_results\MRI\ADNI\mri';

%% 2. Collect image list and filter processed files such as y_ / w_.
img_struct = dir(fullfile(img_dir, '*.nii'));                  % Process .nii files only.
names      = {img_struct.name};
keep_mask  = ~startsWith(names, {'y_', 'w_', 'm', 'c', 'o'});  % Adjust filtering rules as needed.
img_struct = img_struct(keep_mask);

%% 3. Build matlabbatch.
matlabbatch = {};   % Dynamic expansion.
skip_count  = 0;

for i = 1:numel(img_struct)
    img_name = img_struct(i).name;
    def_name = ['y_' img_name];                                % Match deformation field.
    def_path = fullfile(def_dir, def_name);
    img_path = fullfile(img_dir, img_name);

    if ~isfile(def_path)
        fprintf(2, 'Missing deformation field, skipped: %s\n', img_name);
        skip_count = skip_count + 1;
        continue;
    end

    k = numel(matlabbatch) + 1;                                % Next batch unit.
    matlabbatch{k}.spm.spatial.normalise.write.subj.def      = {def_path};
    matlabbatch{k}.spm.spatial.normalise.write.subj.resample = {[img_path ',1']};

    % Write options. Keep consistent with previous settings or modify as needed.
    matlabbatch{k}.spm.spatial.normalise.write.woptions.bb     = [-90 -126 -72; 90 90 108];
    matlabbatch{k}.spm.spatial.normalise.write.woptions.vox    = [1.5 1.5 1.5];
    matlabbatch{k}.spm.spatial.normalise.write.woptions.interp = 4;
    matlabbatch{k}.spm.spatial.normalise.write.woptions.prefix = 'w';
end

fprintf('\nFound %d images, matched %d images, missing %d deformation fields.\n', ...
        numel(img_struct)+skip_count, numel(matlabbatch), skip_count);

if isempty(matlabbatch)
    error('No processable paired files were found. Script terminated.');
end

%% 4. Run SPM batch processing.
spm('defaults', 'FMRI');
spm_jobman('run', matlabbatch);

fprintf('\nAll files have been written to MNI space (output prefix "w").\n');
