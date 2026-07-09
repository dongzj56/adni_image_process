% Split 4D images.

% Specify the root directory.
root_dir = "D:\ADNI_PET\ADNI"; 

% Specify the output directory.
% Leave it empty to overwrite original files.
output_dir = 'D:\ADNI_PET\ADNI\3D-1';  
% output_dir = [];  
if ~isempty(output_dir) && ~exist(output_dir, 'dir')
    mkdir(output_dir);  % Create the output directory if it does not exist.
end

% TODO
volume_to_keep=1; % Use 0 to keep all volumes.

Fun_Split_4DTo3D(root_dir,output_dir,volume_to_keep)
