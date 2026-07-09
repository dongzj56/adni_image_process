function coregister_job(ref,source,interp,outputPrefix,verbose)
    if nargin < 4 || isempty(outputPrefix)
        prefix = 'r';
    end
    if nargin < 5
        verbose = true;
    end
    % Create the matlabbatch structure.
    matlabbatch{1}.spm.spatial.coreg.estwrite.ref = {ref}; % Set reference image.
    matlabbatch{1}.spm.spatial.coreg.estwrite.source = {source}; % Set source image.
    matlabbatch{1}.spm.spatial.coreg.estwrite.other = {''}; % Empty value means there are no other images.
    matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.cost_fun = 'nmi'; % Use NMI as the cost function.
    matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.sep = [4 2]; % Registration resolution: 4 mm and 2 mm.
    matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001]; % Tolerance.
    matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.fwhm = [7 7]; % Smoothing: 7 mm.
    matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.interp = interp; % Cubic interpolation.
    matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.wrap = [0 0 0]; % No wrapping.
    matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.mask = 0; % Do not apply a mask.
    matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.prefix = outputPrefix; % Set output file prefix.
    % Run the job.
    % Use evalc to suppress printed output from spm_jobman.
    if verbose
        spm_jobman('run', matlabbatch); % Run the registration job.
    else
        evalc('spm_jobman(''run'', matlabbatch);');
    end
end

