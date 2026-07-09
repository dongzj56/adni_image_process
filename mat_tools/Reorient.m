% If an error occurs, uncomment the line below and retry after adding the SPM path.
spm('Defaults', 'fMRI');        % Set SPM defaults.
spm_jobman('initcfg');          % Initialize the job manager.

p=spm_select(Inf,'.nii');
%i_type = 't1'; % use default: T1canonical, MRI：t1/t2
i_type = 't1'; % use default: T1canonical, MRI：t1/t2
center_origin = true;

% Open the log file for writing; create it if it does not exist.
logFile = 'Failed_auto_reorient.txt';
fid = fopen(logFile, 'w+'); % Write mode.
if fid == -1
    error('Cannot open log file: %s', logFile);
end

%% RUN
auto_reorient(p,i_type,center_origin,fid)

%%
function auto_reorient(p,i_type,center_origin,fid) 
    % Check input.
    if nargin<1 || isempty(p)
        return
    end
    if iscell(p), p = char(p); end
    Np = size(p,1);
    
    if nargin<2 || isempty(i_type)
        i_type = 'T1canonical';
    end
    
    if nargin<3
        center_origin = true;
    end


    %% Specify template.
    switch lower(i_type)
        case 't1',
            tmpl = fullfile(spm('dir'),'toolbox','OldNorm','T1.nii');
        case 't2', 
            tmpl = fullfile(spm('dir'),'toolbox','OldNorm','T2.nii');
        case 'epi', 
            tmpl = fullfile(spm('dir'),'toolbox','OldNorm','EPI.nii');
        case 'pd', 
            tmpl = fullfile(spm('dir'),'toolbox','OldNorm','PD.nii');
        case 'pet', 
            tmpl = fullfile(spm('dir'),'toolbox','OldNorm','PET.nii');
        case 'spect', 
            tmpl = fullfile(spm('dir'),'toolbox','OldNorm','SPECT.nii');
        case 't1canonical', 
            tmpl = fullfile(spm('dir'),'canonical','single_subj_T1.nii');
        otherwise, error('Unknown image type')
    end

    % Read template.
    vg=spm_vol(tmpl);
    flags.regtype='rigid';
    %p=spm_select(inf,'image');
    num_err = 0;
    num_done = 0;
    for i=1:size(p,1)
        f=strtrim(p(i,:));
        if center_origin
            %% Set the origin to the center of the image
            % Move the image AC point to the image center.
            file = deblank(f); % Remove trailing whitespace from the path.
            st.vol = spm_vol(file);% Store image metadata in st.vol.
            vs = st.vol.mat\eye(4);% Compute the coordinate transform matrix in image space.
            % Set the last column of vs, which represents translation, to the image center.
            % st.vol.dim is the image dimension, for example [x, y, z].
            vs(1:3,4) = (st.vol.dim+1)/2; 
            % Update the image spatial transform information.
            % Use inv(vs) to write the updated spatial information to the file.
            spm_get_space(st.vol.fname,inv(vs)); 
        end
        try
            spm_smooth(f,'temp.nii',[12 12 12]);
            vf=spm_vol('temp.nii');
            [M,scal] = spm_affreg(vg,vf,flags);
            M3=M(1:3,1:3);
            [u s v]=svd(M3);
            M3=u*v';
            M(1:3,1:3)=M3;
            N=nifti(f);
            N.mat=M*N.mat;
            create(N);
            % fprintf('Successfully processed file: \n%s\n',f);
            num_done = num_done + 1;
            fprintf('processing file Done(All): %d(%d)\n',num_done,size(p,1));
        catch ME
            num_err = num_err + 1;
            fprintf('Failed to process file: \n%s\n',f)
            fprintf('Failed to process file: \n%s\n',ME.message)
            fprintf(fid, 'Failed to process file:\n%s\n', f); % Write failure information to the log.
            fprintf(fid, '\n'); % Newline.
            fprintf(fid, repmat('=', 1, 20)); % Write 20 equal signs.
        end
    end
    fprintf('Number of file successed to process: %d\n',size(p,1))
    fprintf('Number of file Failed to process: %d\n',num_err)
    delete('temp.nii');
    % Close the log file.
    fclose(fid);
end


