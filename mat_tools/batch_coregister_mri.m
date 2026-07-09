% If an error occurs, uncomment the lines below to add SPM to the path and retry.
% You can also type spm in the command window and retry.
% spm('Defaults', 'fMRI'AAL);        % Set SPM defaults.
% spm_jobman('initcfg');          % Initialize the job manager.
% MRI => MNI
% PET => MRI,PET => ROI
MNI = 'E:\ADNI_dataset_902_samples\AAL_template\AAL3v2_for_SPM12\AAL3\AAL3v1_1mm.nii';
MRI = 'E:\ADNI_dataset_902_samples\05-mask_processed_whole_brain\MRI_MNI_1mm-normal';  

outputPrefix = 'r'; % Prefix for completed files.
verbose = 0; % Print SPM output for error checking.

% Suppress PS print warnings if SPM graphics are enabled.
% print('-dpdf', 'output.pdf');

%run
batch_coregiter_job(MNI,MRI,outputPrefix,verbose);  

function batch_coregiter_job(MNI,MRI,outputPrefix,verbose,interp)
    if nargin<5 interp = 4; end

    % Get .nii files that do not start with the output prefix.
    mni = [MNI,',1'];
    %%
    MRI_files = dir(fullfile(MRI, '*.nii'));

    processed_files = MRI_files(startsWith({MRI_files.name}, outputPrefix));
    processed_names = cellfun(@(x) extractAfter(x, strlength(outputPrefix)), {processed_files.name}, 'UniformOutput', false);

    MRI_files = MRI_files(~startsWith({MRI_files.name}, outputPrefix));
    MRI_files = MRI_files(~ismember({MRI_files.name}, processed_names));


    fprintf('Total file counts - MRI: %d\n',numel(MRI_files)+numel(processed_names));
    fprintf('Pending file counts - MRI: %d\n',numel(MRI_files));

    currentDir = pwd;
    tempName = 'temp.nii';
    rtempName = [outputPrefix,tempName];
    tempFilePath = fullfile(currentDir,tempName);
    rtempFilePath = fullfile(currentDir,rtempName);

    for i = 1:numel(MRI_files)
        m = fullfile(MRI, MRI_files(i).name);
        % copyfile(m, tempFilePath);
        coregister_job(mni,m, interp, outputPrefix,verbose); % Register MRI to MNI.
        % movefile(rtempFilePath,fullfile(MRI,[outputPrefix,MRI_files(i).name])); 
        fprintf('Done(All): %d(%d),Processing... \n',i,numel(MRI_files)); 
    end
    delete(tempFilePath);
end



