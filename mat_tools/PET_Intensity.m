% NO Complete!!!
clc,clear;
roi = 'test/aal3.nii';
pet = 'test';
s_info = 'Info/Web_BOTH_MRI_PET.csv';
get_pet_data(roi,pet,'',s_info)
function get_pet_data(mask_path,pet_dir,roi_info,subject_info,Vox_mm3,SUVr,cerebellar,startswith,output_csv)
    if nargin < 4 subject_info = ''; end
    if nargin < 6 SUVr = 1; end
    if nargin < 5 Vox_mm3 = 1; end
    if nargin < 7 cerebellar = 0; end
    if nargin < 8 startswith = 'wr'; end
    if nargin < 9 output_csv = 'PET_DATA.csv'; end

    % Initialize parameters.
    ID = 'Subject ID';
    Injected_dose = 185;  % MBq, FDG-PET Reference ADNI
    cerebellar_ID = 95:112;  % Cerebellar region IDs.
    % cerebellar_ID = 95:120;  % Cerebellar region IDs.

    roi_info = load_roi_info('Template/ROITemplate/aal3.csv',1,';');
    header = get_header(roi_info, Vox_mm3, SUVr);
    if SUVr
        if ~isempty(subject_info)
            % s_info = readtable(subject_info,'VariableNamingRule','preserve');
            s_info = readtable(subject_info, 'VariableNamingRule', 'preserve', 'TreatAsEmpty', {'NA', 'N/A', ''});
            s_info = s_info(strcmp(s_info.Modality, 'PET'), :);
        else
            disp('Calculating SUVr requires the subject_info weight parameter');
            return;
        end
    end
    
    % Open the output file.
    fid = fopen(output_csv, 'w');
    % Get the NIfTI file list.
    nii_files = dir(fullfile(pet_dir, [startswith, '*.nii*']));
    

    header = get_header(roi_info, Vox_mm3, SUVr);
    fprintf(fid, '%s\n', strjoin(header, ';'));

    mask = niftiread(mask_path);
    roi_V = spm_vol(mask_path);
    data = spm_read_vols(roi_V); % Read data before changing the name.
    roi_affine  = roi_V.mat;
    unique_values = unique(mask(mask ~= 0));  % Get unique mask values, excluding 0.
    indices = find(data == 1);
    [rows, cols, slices] = ind2sub(size(data), indices);
    % Use the affine matrix if indices need to be converted to physical-space coordinates.
    % Example: get physical coordinates (x, y, z).
    inverse_affine = inv(roi_affine);
    physical_coords = roi_affine * [rows'; cols'; slices'; ones(1, numel(rows))];
    % physical_coords(1, :) is x, physical_coords(2, :) is y, and physical_coords(3, :) is z.
    voxel_coords = inverse_affine * [physical_coords];
    % intensity = nii(sub2ind(size(nii), rows, cols, slices));
    for i = 1:length(nii_files)

        ce_suv = 1;
        weight = -1;

        nii_filename = nii_files(i).name;
        nii_path = fullfile(pet_dir, nii_filename);
        nii = niftiread(nii_path);  % Read the NIfTI file.

        indices = find(mask == ci);

        
        % Calculate SUVr.
        if SUVr
            [~, sid] = fileparts(nii_filename);
            sid = sid(length(prefix)+1:end);  % Get subject ID.
            weight_idx = strcmp(s_info.(ID), sid);
            if any(weight_idx)
                weight = s_info.Weight(weight_idx) * 1000;  % Weight in grams.
            else
                disp([sid, ' has no weight information. SUVr may be 0']);
            end
            
            sum_ce = 0;
            for ci = cerebellar_ID
                indices = find(mask == ci);
                ce_vox_in = nii(indices);  % Get voxel values in cerebellar regions.
                sum_ce = sum_ce + sum(ce_vox_in);
            end
            ce_suv = sum_ce / (Injected_dose / weight);
        end
        
        % Calculate the mean value and other features for each ROI.
        average_values = {};
        for value = fieldnames(roi_info)'
            value = value{1};
            avg_intensity = 0;
            vox_mm3 = 0;
            roi_suvr = 0;
            
            if ~ismember(value, unique_values) || (ismember(value, cerebellar_ID) && ~cerebellar)
                continue;
            else
                indices = find(mask == value);
                intensity = nii(indices);
                avg_intensity = mean(intensity);
                sum_intensity = sum(intensity);
                
                vox_mm3 = numel(indices);
                roi_suv = sum_intensity / (Injected_dose / weight);
                roi_suvr = roi_suv / ce_suv;
            end
            
            average_values = [average_values, {num2str(avg_intensity)}];
            if Vox_mm3
                average_values = [average_values, {num2str(vox_mm3)}];
            end
            if SUVr
                average_values = [average_values, {num2str(roi_suvr)}];
            end
        end
        
        % Write to CSV.
        fprintf(fid, '%s,%s\n', nii_filename, strjoin(average_values, ','));
    end
    
    % Close the file.
    fclose(fid);
    disp(['Results written to CSV file: ', output_csv]);
end

function roi_info = load_roi_info(roi_csv, header, delimiter, n)
    if nargin < 4 n=200; end
    if nargin < 3 delimiter = ';';  end
    if nargin < 2 header = true; end
    if nargin < 1 roi_csv=''; end

    roi_info = {};

    if ~isempty(roi_csv)
        fid = fopen(roi_csv, 'r');
        % Skip the header if present.
        if header
            fgetl(fid);
        end
        
        tline = fgetl(fid);
        while ischar(tline)
            row = strsplit(tline, delimiter);
            roi_value = str2double(row{1});
            if length(row) < 3 
                row{3} = row{2};
            end
            if length(row) < 4 
                row{4} = row{1};
            end
    
            roi_info{end+1} = {roi_value, row{2}, row{3}, row{4}};
            tline = fgetl(fid);
        end
        fclose(fid);
    else
        for i=1:n
            roi_info{end+1} = {i, ['roi_',i], ['roi_',i], i};
        end
    end 
end

function header = get_header(roi_info, Vox_mm3, SUVr)
    header = {'Subject'};
    for i = 1:numel(roi_info)
        roi_ = roi_info{i};
        roi_name = roi_{2};
        header = [header, roi_name];
        if Vox_mm3
            header = [header, [roi_name, '_Vox_mm3']];
        end
        if SUVr
            header = [header, [roi_name, '_SUVr']];
        end
    end
end
