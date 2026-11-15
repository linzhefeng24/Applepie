% getNumPreSyn.m
%
% Helper function that gets the number of synapses one or more neurons
%  makes onto a specified target neuron (all specified by name)
%
% INPUTS:
%   sourceNeurons - presynaptic neuron(s), by name, as single string or
%       cell array
%   targetNeuron - single string of name of target neuron
%   connGraph - digraph object of connectivity. Requires number of synapses
%       field of edges to be named 'NumSyn'
%
% OUTPUTS:
%   numSyns - vector of same size as source neurons, with number of
%       synapses between each source neuron and target neuron
%
% CREATED: 3/1/23 - HHY
%
% UPDATED:
%   3/1/23 - HHY
%
function numSyns = getNumPreSyn(sourceNeurons, targetNeuron, connGraph)

    % for multiple source neurons
    if iscell(sourceNeurons)

        % preallocate
        numSyns = zeros(size(sourceNeurons));

        for i = 1:length(sourceNeurons)
            % get shortest path (in number of hops, between source and
            %  target neurons
            [~, ~, edgeInd] = shortestpath(connGraph, sourceNeurons{i},...
                targetNeuron, 'Method', 'unweighted');
            
            % check that this is a monosynaptic connection
            % otherwise, value will remain 0
            if (length(edgeInd) == 1)
                numSyns(i) = connGraph.Edges.NumSyn(edgeInd);
            end
        end
    else % for one source neuron
        [~, ~, edgeInd] = shortestpath(connGraph, sourceNeurons,...
            targetNeuron, 'Method', 'unweighted');
        
        % check that this is a monosynaptic connection
        % otherwise, value will remain 0
        if (length(edgeInd) == 1)
            numSyns = connGraph.Edges.NumSyn(edgeInd);
        else
            numSyns = 0;
        end
    end

end