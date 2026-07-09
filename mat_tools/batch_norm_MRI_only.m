% 1. Image folder (193 x 229 x 193 or another size).
MRI_DIR = 'F:\ADNI_dataset_902_samples\05-mask_processed_whole_brain\MRI_MNI_193_229_193';

% 2. Deformation-field folder for the same subject batch.
DEF_DIR = 'F:\ADNI_dataset_902_samples\04-MRI_skull_stripping_results\MRI\ADNI\mri';

batch_reslice_mri_job(MRI_DIR, DEF_DIR, 'wr', 0, 4);     % Produces wr*.nii.

function batch_reslice_mri_job(MRI_DIR, DEF_DIR, outputPrefix, verbose, interp)
% Use existing y_*.nii files to resample MRI to MNI (113 x 137 x 113, 1.5 mm3).
% -------------------------------------------------------------------------
% MRI_DIR      Directory containing T1 images to resample (*.nii).
% DEF_DIR      Directory containing matching y_*.nii files; can differ from MRI_DIR.
% outputPrefix Prefix for MNI-space output files. Default: 'wr'.
% verbose      0/1: detailed SPM output. Default: 0.
% interp       0-7: interpolation method. Default: 4 (cubic).
%
% Dependency: normalise_job.m, which controls bb / vox / prefix.
% -------------------------------------------------------------------------

if nargin < 3 || isempty(outputPrefix), outputPrefix = 'wr'; end
if nargin < 4 || isempty(verbose),      verbose = 0;        end
if nargin < 5 || isempty(interp),       interp  = 4;        end

spm('Defaults','fMRI');  spm_jobman('initcfg');

fid = fopen('err_mri_reslice.log','w+');      % Record missing files or errors.
if fid == -1, error('Unable to write log file'); end

allMRI = dir(fullfile(MRI_DIR,'*.nii'));
done   = startsWith({allMRI.name}, outputPrefix);
TODO   = allMRI(~done);

fprintf('Total MRI: %d | Pending: %d\n', numel(allMRI), numel(TODO));

for k = 1:numel(TODO)
    mriFile   = TODO(k).name;
    srcPath   = fullfile(MRI_DIR, mriFile);

    % ---- Find the matching y_*.nii in DEF_DIR by filename. ----
    % Strip prefixes such as wr / r / m to get the base filename.
    [~, baseName, ~] = fileparts(mriFile);
    baseName = regexprep(baseName, '^[a-z]+', '');   % Remove leading prefix letters.
    cand = dir(fullfile(DEF_DIR, ['y_*', baseName, '*.nii']));
    if isempty(cand)
        fprintf(fid, '[Missing y_] %s\n', mriFile);
        warning('[Missing y_] %s skipped', mriFile);
        continue;
    end
    defPath = fullfile(DEF_DIR, cand(1).name);       % Use the first match.

    fprintf('[%3d/%3d] %s  ←  %s\n', k, numel(TODO), mriFile, cand(1).name);

    try
        % Call the helper to write the output (113 x 137 x 113, 1.5 mm3).
        normalise_job(defPath, srcPath, interp, outputPrefix, verbose);
    catch ME
        fprintf(fid, '[Normalise Error] %s: %s\n', mriFile, ME.message);
        warning('[Normalise Error] %s recorded', mriFile);
    end
end

fclose(fid);
fprintf('\nAll processing complete. Output file prefix: "%s"\n', outputPrefix);
end
