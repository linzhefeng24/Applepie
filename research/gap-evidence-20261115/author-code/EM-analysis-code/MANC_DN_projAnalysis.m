% MANC_DN_projAnalysis.m
%
% Quick script to read in MANC_legDNs.csv and classify leg neuromere
%  projecting DNs

synThresh = 0;

filePath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/VNC/MANC_legDNs.csv';
outFilePath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/VNC/MANC_legDNs_cat.csv';

legDNMat = readtable(filePath);

numLegDNs = size(legDNMat,1);

% preallocate vectors for output info
uniBi = repmat("",numLegDNs,1);
numLegNeuroL = zeros(numLegDNs,1);
numLegNeuroR = zeros(numLegDNs,1);

% get info on each DN
for i = 1:numLegDNs
    % check if DN is unilaterally or bilaterally projecting
    numLOut = legDNMat.T1L_Pre(i) + legDNMat.T2L_Pre(i) + ...
        legDNMat.T3L_Pre(i);
    numROut = legDNMat.T1R_Pre(i) + legDNMat.T2R_Pre(i) + ...
        legDNMat.T3R_Pre(i);
    % projects both left and right
    if (numLOut > synThresh && numROut > synThresh)
        uniBi(i) = "bi";
    else
        uniBi(i) = "uni";
    end

    % number of leg neuromeres on left
    % outputs in all 3
    if (legDNMat.T1L_Pre(i) > synThresh && ...
            legDNMat.T2L_Pre(i) > synThresh && ...
        legDNMat.T3L_Pre(i) > synThresh)
        numLegNeuroL(i) = 3;
    % outputs in 2    
    elseif (legDNMat.T1L_Pre(i) > synThresh && ...
            legDNMat.T2L_Pre(i) > synThresh)
        numLegNeuroL(i) = 2;
    elseif (legDNMat.T2L_Pre(i) > synThresh && ...
            legDNMat.T3L_Pre(i) > synThresh)
        numLegNeuroL(i) = 2;
    elseif (legDNMat.T1L_Pre(i) > synThresh && ...
            legDNMat.T3L_Pre(i) > synThresh)
        numLegNeuroL(i) = 2;
    % outputs in 1    
    elseif (legDNMat.T1L_Pre(i) > synThresh)
        numLegNeuroL(i) = 1;
    elseif (legDNMat.T2L_Pre(i) > synThresh)
        numLegNeuroL(i) = 1;
    elseif (legDNMat.T3L_Pre(i) > synThresh)
        numLegNeuroL(i) = 1;
    % no outputs    
    else
        numLegNeuroL(i) = 0;
    end

    % number of leg neuromeres on left
    % outputs in all 3
    if (legDNMat.T1R_Pre(i) > synThresh && ...
            legDNMat.T2R_Pre(i) > synThresh && ...
        legDNMat.T3R_Pre(i) > synThresh)
        numLegNeuroR(i) = 3;
    % outputs in 2    
    elseif (legDNMat.T1R_Pre(i) > synThresh && ...
            legDNMat.T2R_Pre(i) > synThresh)
        numLegNeuroR(i) = 2;
    elseif (legDNMat.T2R_Pre(i) > synThresh && ...
            legDNMat.T3R_Pre(i) > synThresh)
        numLegNeuroR(i) = 2;
    elseif (legDNMat.T1R_Pre(i) > synThresh && ...
            legDNMat.T3R_Pre(i) > synThresh)
        numLegNeuroR(i) = 2;
    % outputs in 1    
    elseif (legDNMat.T1R_Pre(i) > synThresh)
        numLegNeuroR(i) = 1;
    elseif (legDNMat.T2R_Pre(i) > synThresh)
        numLegNeuroR(i) = 1;
    elseif (legDNMat.T3R_Pre(i) > synThresh)
        numLegNeuroR(i) = 1;
    % no outputs    
    else
        numLegNeuroR(i) = 0;
    end
end

% categories of DNs
DNclass = repmat("",numLegDNs,1);

% unilateral, projects to all 3 leg neuromeres on 1 side: u3
DNclass((strcmpi(uniBi,"uni") & (numLegNeuroL == 3)) | ...
    (strcmpi(uniBi,"uni") & (numLegNeuroR == 3))) = "u3";

% unilateral, projets to 2 leg neuromeres on 1 side: u2
DNclass((strcmpi(uniBi,"uni") & (numLegNeuroL == 2)) | ...
    (strcmpi(uniBi,"uni") & (numLegNeuroR == 2))) = "u2";

% unilateral, projects to 1 leg neuromere: u1
DNclass((strcmpi(uniBi,"uni") & (numLegNeuroL == 1)) | ...
    (strcmpi(uniBi,"uni") & (numLegNeuroR == 1))) = "u1";

% bilateral, projects to all 6 leg neuromeres: b6
DNclass((strcmpi(uniBi,"bi") & (numLegNeuroL == 3) & (numLegNeuroR == 3))) ...
    = "b6";

% bilateral, projects to 2 leg neuromeres: b2
DNclass((strcmpi(uniBi,"bi") & (numLegNeuroL + numLegNeuroR == 2))) = "b2";

% bilateral, projects to not 6 or 2 leg neuromeres: bs
DNclass((strcmpi(uniBi,"bi") & (numLegNeuroL + numLegNeuroR ~= 2) & ...
    (numLegNeuroL + numLegNeuroR ~= 6))) = "bs";

% output table
outTableNew = table(uniBi, numLegNeuroL, numLegNeuroR, ...
    DNclass,'VariableNames',{'uni/bi','num L neuromeres', ...
    'num R neuromeres', 'DN class'});
outTable = [legDNMat outTableNew];

writetable(outTable,outFilePath);

% print to screen, some numbers
fprintf('Number of unilateral DNs that project to all 3 leg neuromeres: %d\n', ...
    sum(strcmpi(DNclass,"u3")));
fprintf('Number of unilateral DNs that project to 2 leg neuromeres: %d\n', ...
    sum(strcmpi(DNclass,"u2")));
fprintf('Number of unilateral DNs that project to 1 leg neuromere: %d\n', ...
    sum(strcmpi(DNclass,"u1")));
fprintf('Number of bilateral DNs that project to all 6 leg neuromeres: %d\n', ...
    sum(strcmpi(DNclass,"b6")));
fprintf('Number of bilateral DNs that project to 2 leg neuromeres: %d\n', ...
    sum(strcmpi(DNclass,"b2")));
fprintf('Number of bilateral DNs that project to not 2 or 6 leg neuromeres: %d\n', ...
    sum(strcmpi(DNclass,"bs")));
