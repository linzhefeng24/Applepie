% getNumPostSyn.m
%
% Helper function that gets the number of synapses one neuron makes onto
%  specified target neuron(s) (all specified by name)
%
% INPUTS:
%   sourceNeuron - presynaptic neuron, by name, as single string
%   targetNeurons - postsynaptic neurons, by name, as single string or cell
%       array
%   connGraph - digraph object of connectivity. Requires number of synapses
%       field of edges to be named 'NumSyn'
%
% OUTPUTS:
%   numSyns - vector of same size as target neurons, with number of
%       synapses between each source neuron and target neuron
%
% CREATED: 9/7/23 - HHY
%
% UPDATED:
%   9/7/23 - HHY
%
function numSyns = getNumPostSyn(sourceNeuron, targetNeurons, connGraph)

    % for multiple target neurons
    if iscell(targetNeurons)

        % preallocate
        numSyns = zeros(size(targetNeurons));

        for i = 1:length(targetNeurons)
            % get shortest path (in number of hops, between source and
            %  target neurons
            [~, ~, edgeInd] = shortestpath(connGraph, sourceNeuron,...
                targetNeurons{i}, 'Method', 'unweighted');
            
            % check that this is a monosynaptic connection
            % otherwise, value will remain 0
            if (length(edgeInd) == 1)
                numSyns(i) = connGraph.Edges.NumSyn(edgeInd);
            end
        end
    else % for one source neuron
        [~, ~, edgeInd] = shortestpath(connGraph, sourceNeuron,...
            targetNeurons, 'Method', 'unweighted');
        
        % check that this is a monosynaptic connection
        % otherwise, value will remain 0
        if (length(edgeInd) == 1)
            numSyns = connGraph.Edges.NumSyn(edgeInd);
        else
            numSyns = 0;
        end
    end

end