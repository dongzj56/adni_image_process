% If an error occurs, uncomment the lines below to add SPM to the path and retry.
% You can also type spm in the command window and retry.
spm('Defaults', 'fMRI');        % Set SPM defaults.
spm_jobman('initcfg');          % Initialize the job manager.

% MRI => seg MRI (MRI/mri)
% PET => MRI,PET => MNI(def spital register)
PET = 'F:\ADNI_dataset_902_samples\03-ACPC_corrected\pet\ADNI';
MRI = 'F:\ADNI_dataset_902_samples\04-MRI-CAT12_results\MRI\ADNI\mri'; % Segmented MRI data are in the mri directory.

outputPrefix = 'wr'; % Prefix for completed files.
verbose = 0; % Print SPM output for error checking.
interp = 4;

% Define the log file path.
logFile = 'err_coregister.log';

% Open the log file. Existing files are overwritten.
fid = fopen(logFile, 'w+');
if fid == -1
    error('Unable to open log file %s for writing', logFile);
end

% Suppress PS print warnings if SPM graphics are enabled.
% print('-dpdf', 'output.pdf');

%run
batch_coregiter_job(PET,MRI,outputPrefix,verbose,fid);  

function batch_coregiter_job(PET,MRI,outputPrefix,verbose,fid,interp)
    if isempty(outputPrefix) outputPrefix = 'wr'; end
    if nargin<6
        interp = 1;
    end
    %%
    % Get .nii files that do not start with the output prefix.
    PET_files = dir(fullfile(PET, '*.nii'));
    MRI_files = dir(fullfile(MRI, '*.nii'));

    processed_files = PET_files(startsWith({PET_files.name}, outputPrefix));
    processed_names = cellfun(@(x) extractAfter(x, strlength(outputPrefix)), {processed_files.name}, 'UniformOutput', false);

    PET_files = PET_files(~(startsWith({PET_files.name}, outputPrefix)));
    PET_files = PET_files(~ismember({PET_files.name}, processed_names));

    fprintf('Total file counts - PET: %d\n',numel(PET_files)+numel(processed_names));
    fprintf('Pending file counts - PET: %d\n',numel(PET_files));

    currentDir = pwd;
    tempName = 'temp.nii';
    rtempName = [outputPrefix,tempName];
    tempFilePath = fullfile(currentDir,tempName);
    rtempFilePath = fullfile(currentDir,rtempName);
    % Iterate over PET files and find matching MRI files.
    for i = 1:length(PET_files)
        %% 
        [~,subject_id,~] = fileparts(PET_files(i).name);
        seg_mri_name = ['p0',PET_files(i).name];
        % seg_mri_name = ['p0','r',PET_files(i).name]
        %%
        MRI_files = dir(MRI); 
        matching_files = MRI_files(startsWith({MRI_files.name}, 'p0') ...
            & contains({MRI_files.name}, subject_id));
        if numel(matching_files) > 0
            seg_mri_name = matching_files(1).name;
        end
        mri_name = extractAfter(seg_mri_name, strlength('p0'));
        def = ['y_', mri_name];

        m = fullfile(MRI,seg_mri_name);
        p = fullfile(PET, PET_files(i).name);
        d = fullfile(MRI,def);
        if exist(m) & exist(d)
            copyfile(p, tempFilePath);
            % Step 1: register PET to mwp1MRI.
            coregister_job(m, tempFilePath, interp, outputPrefix, verbose); 
            copyfile(rtempFilePath, tempFilePath);
            normalise_job(d,tempFilePath,interp,outputPrefix,verbose);
            % cor_pet = sprintf('%s%s_%s%s',outputPrefix,roi_name,PET_files(i).name);
            movefile(rtempFilePath,fullfile(PET,[outputPrefix,PET_files(i).name])); % or  cor_pet
        else
            fprintf(fid, 'No MRI file matched the PET file: %s\n', m);
            warning('No MRI file matched the PET file: %s\n', m);
        end
        fprintf('Done(All): %d(%d),Processing... \n',i,length(PET_files)); 
    end

    delete(tempFilePath);
    % Close the log file.
    fclose(fid);
end
