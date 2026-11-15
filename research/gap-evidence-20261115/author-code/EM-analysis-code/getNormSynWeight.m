% getNormSynWeight.m
%
% Function to get normalized weights: number of synapses of given
%  connection / number of synapses that neuron receives
%
% INPUTS:
%   synNumCSVFile - full path to CSV file containing node IDs and number of
%       synapses they receive
%   t - array of targets for connections
%   weights - array of weights for each connection
%
% OUTPUTS:
%   normWeights - array of normalized weights
%
% CREATED: 1/3/22 - HHY
%
% UPDATED:
%   1/3/22 - HHY
%
function normWeights = getNormSynWeight(synNumCSVFile, t, weights)
    
    synNumCSVFileContents = readmatrix(synNumCSVFile, 'NumHeaderLines', 0, ...
            'Delimiter', ',', 'OutputType', 'char');
    
    synNumNames = synNumCSVFileContents(:,1);
    synNumInputs = synNumCSVFileContents(:,2);
    synNumInputs = str2double(synNumInputs);
    
    normWeights = nan(size(weights));
    
    for i = 1:length(normWeights)
    
        thisName = t{i};
    
        % if in the list
        if (any(strcmp(thisName, synNumNames)))
            % get index
            synNumInd = find(strcmpi(thisName, synNumNames),1);
            thisSynNum = synNumInputs(synNumInd);
    
            % update weights
            normWeights(i) = weights(i) / thisSynNum;
        end
    end
end