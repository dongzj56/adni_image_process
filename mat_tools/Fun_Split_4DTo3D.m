function [] = Fun_Split_4DTo3D(root_dir,output_dir,volume_to_keep)
   
   % Initialize a table to store data.
    results = table();
    % Get all NIfTI files.
    nii_files = dir(fullfile(root_dir, '**', '*.nii'));  % Traverse all subdirectories.

    % Iterate over each NIfTI file.
    fprintf('Processing 4D file...\n');
    for i = 1:length(nii_files)
        % Get the full file path.
        nii_path = fullfile(nii_files(i).folder, nii_files(i).name);
        % Use part of the original filename as the new filename.
        [~, Modality, ~] = fileparts(nii_files(i).folder); % Get the last-level directory name.
        m_out_dir = fullfile(output_dir,Modality);
        if ~exist(m_out_dir, 'dir')
            mkdir(m_out_dir); % Create the folder; skip if it already exists.
        end
        
        [~, name, ~] = fileparts(nii_files(i).name);
        % Load file information.
        V = spm_vol(nii_path);

        % Check whether this is a 4D file.
        if numel(V) > 1
            % fprintf('Processing 4D file: %s\n', nii_path);
            % Split the 4D file.
            Vo = spm_file_split(nii_path);

            if volume_to_keep > numel(Vo)
                fprintf('volume_to_keep:%d > numel(Vo):%d\n', volume_to_keep, numel(Vo));
                return
            end
           
            % Keep only the specified volume and delete the others.
            for j = 1:numel(Vo) 
                old_filename = Vo(j).fname;  % Original filename.
                if volume_to_keep == 0 && ~isempty(output_dir)
                    [~, name, ~] = fileparts(Vo(j).fname);
                    new_filename = fullfile(m_out_dir,strcat(name,'.nii'));  % New filename.
                    movefile_with_error_handling(old_filename, new_filename)
                % Keep only the specified volume.
                elseif  j == volume_to_keep
                    % Determine the output directory.
                    if isempty(output_dir)
                        output_dir = nii_files(i).folder;  % Use the original file directory.
                    end
                    new_filename = fullfile(m_out_dir,strcat(name,'.nii'));  % New filename.
                    movefile_with_error_handling(old_filename, new_filename)

                else
                    delete_with_error_handling(old_filename)
                end
            end
            results = [results; table({name}', {Modality}', 'VariableNames', {'Subject', 'Modality'})];
        else
            new_filename = fullfile(m_out_dir,strcat(name,'.nii'));  % New filename.
            copyfile(nii_path, new_filename);
        end
        

    end
    fprintf('Over Processing 4D file...\n');
    % Write results to a CSV file.
    writetable(results, fullfile(output_dir, 'Split_4DTo3D.csv'));
end


function movefile_with_error_handling(old_filename, new_filename)
    try
        movefile(old_filename, new_filename);
    catch ME
        fprintf('Error renaming %s to %s: %s\n', old_filename, new_filename, ME.message);
    end
end

function delete_with_error_handling(old_filename)
    try
        delete(old_filename);
    catch ME
        fprintf('Error deleting %s: %s\n', old_filename, ME.message);
    end
end
