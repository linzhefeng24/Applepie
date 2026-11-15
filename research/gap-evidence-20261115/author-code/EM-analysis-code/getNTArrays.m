% getNTArrays.m
%
% Function to generate digraph arrays for neurons' neurotransmitter 
%  (info for both nodes and edges)
%
% INPUTS:
%   ntFolder - full path to folder of neurotransmitter txt files
%   s - array of source nodes for digraph
%   names - array of node names for digraph
%
% OUTPUTS:
%   ntEdges - neurotransmitter for each edge; empty array if unknown
%   neurotransNodes - neurotransmitter for each node; empty if unknown
%   ntprctNodes - percent of synapses for neuron predicted to belong to
%       that NT
%
% CREATED: 2/28/23 - HHY
%
% UPDATED:
%   2/28/23 - HHY
%
function [ntEdges, neurotransNodes, ntprctNodes] = getNTArrays(ntFolder,...
    s, names)

    % get names of all neurotransmitter files
    ntCSVNames = dir([ntFolder filesep '7*.txt']);

    % preallocate
    neurotransNodes = repmat({''},size(names));
    ntprctNodes = zeros(size(names));
    ntEdges = repmat({''},size(s));

    % loop through all neurotransmitter files; name is source neuron
    for i = 1:length(ntCSVNames)
        % get neuron ID (file name without .txt)
        thisNeuronID = ntCSVNames(i).name;
        thisNeuronID = thisNeuronID(1:(end-4));

        % get neurotransmitter prediction and percentage
        [thisPredNT, thisPredNTprct, ~, ~] = readNTFlyWire(...
            thisNeuronID, ntFolder);

        % update output arrays
        % get node index for this source neuron
        nodeInd = find(strcmpi(thisNeuronID, names));

        % update node with neurotransmitter info
        if ~isempty(nodeInd)
            neurotransNodes(nodeInd) = thisPredNT;
            ntprctNodes(nodeInd) = thisPredNTprct;
        end

        % get edges
        edgeInds = find(strcmpi(thisNeuronID, s));

        % loop through all edges with this neuron as source, update NT
        for j = 1:length(edgeInds)
            ntEdges(edgeInds(j)) = thisPredNT;
        end
    end
end