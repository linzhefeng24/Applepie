% readNTFlyWire.m
%
% Function to read neurotransmitter text file created using
%  getNTpredFlywire.r. Takes in path to folder containing all NT text files
%  and neuron ID and returns number of output synapses, predicted NT, and
%  the percentage of synapses predicted for the 6 NT types (ACh, Glu, GABA,
%  octopamine, serotonin, dopamine)
%
% INPUTS:
%   neuronID - neuron ID, as string
%   folderPath - full path to folder containing all NT text files
%
% OUTPUTS:
%   predNT - predicted neurotransmitter, as string: ACh, Glu, GABA, Oct,
%       5HT, or DA
%   predNTprct - percent of synapses predicted to be for pred NT
%   predNTprctAll - percent of synapses predicted to be each of the 6 NT
%       types, as array in order ACh, Glu, GABA, Oct, 5HT, DA
%   numSyn - number of output synapses for specified neuron 
%
% CREATED: 2/28/23 - HHY
%
% UPDATED:
%   2/28/23 - HHY
%
function [predNT, predNTprct, predNTprctAll, numSyn] = readNTFlyWire(...
    neuronID, folderPath)
    
    % mapping between text file neurotransmitter names and analysis ones
    txtNTNames = {'acetylcholine', 'glutamate', 'gaba', 'octopamine', ...
        'serotonin', 'dopamine'};
    ntNames = {'ACh', 'Glu', 'GABA', 'Oct', '5HT', 'DA'};

    % full path to NT text file
    ntFullPath = [folderPath filesep neuronID '.txt'];

    % read in file
    % open file for reading
    fileID = fopen(ntFullPath, 'r'); 
    % format spec for first line - extracts number of output synapses,
    %  skips neuron ID
    line1FS = 'neuron %*d with %d output synapses:\n';
    % read in first line
    numSyn = fscanf(fileID, line1FS);

    % read in second line, neurotransitter list (for NTs with synapses)
    ntRawList = fgetl(fileID);
    % convert to cell array of strings
    ntList = split(ntRawList);
    ntList(ismissing(ntList)) = []; % remove empty 

    % read last line, gets percentages for neurotransmitters
    ntPrct = fscanf(fileID, '%f');
    % close 
    fclose(fileID); 

    % get predicted neurotransmitter (first of ntList, as they're sorted
    %  with highest percentage first)
    ntInd = find(strcmp(ntList{1}, txtNTNames));
    
    % NT name as analysis one
    predNT = ntNames(ntInd);

    % NT percent (first one)
    predNTprct = ntPrct(1);


    % get percentages for each NT, sorted
    % initialize
    predNTprctAll = zeros(size(txtNTNames'));

    for i = 1:length(ntList)
        thisInd = find(strcmp(ntList{i}, txtNTNames));
        
        predNTprctAll(thisInd) = ntPrct(i);
    end        
end
