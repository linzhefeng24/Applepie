% isPreSyn.m
%
% Function that returns whether each element of a source neuron list is
%  presynaptic to at least x elements of a target neuron list
%
% INPUTS:
%   sourceNeurons - single string or cell array of presynaptic neurons, by
%       name
%   targetNeurons - single string or cell array of potential postsynaptic
%       neurons, by name
%   minNumTargets - minimum number of neurons of targetNeurons each
%       sourceNeuron has to be connected to
%   connGraph - connectivity graph, MATLAB digraph
%
% OUTPUTS:
%   isPreSynLog - logical of size of sourceNeurons, with matched indices,
%       for whether each element is connected to the minimum number of
%       targets
%   numTargetsConn - vector of size of sourceNeurons, with matched indices,
%       for how many elements of targetNeurons each element of
%       sourceNeurons is connected to
%
% CREATED: 9/8/23 - HHY
%
% UPDATED: 
%   9/8/23 - HHY
%
function [isPreSynLog, numTargetsConn] = isPreSyn(sourceNeurons, ...
    targetNeurons, minNumTargets, connGraph)

    % for multiple source neurons
    if iscell(sourceNeurons)

        % preallocate
        isPreSynLog = false(size(sourceNeurons));
        numTargetsConn = zeros(size(sourceNeurons));

        % loop through all source neurons
        for i = 1:length(sourceNeurons)
            % get all successor nodes for this source neuron (direct
            %  targets)
            thisSuccName = successors(connGraph,sourceNeurons{i});

            % compare this list of successor nodes to list of targetNeurons
            if ~isempty(thisSuccName)
                thisNumPostNeurons = 0;
                for j = 1:length(thisSuccName)   
                    % if this successor node is a targetNeuron, increment
                    if any(strcmpi(thisSuccName{j},targetNeurons))
                        thisNumPostNeurons = thisNumPostNeurons + 1;
                    end
                end
                   
                % update logical if meet threshold
                if (thisNumPostNeurons >= minNumTargets)
                    isPreSynLog(i) = true;
                end

                % update num connections
                numTargetsConn(i) = thisNumPostNeurons;
            end
        end
                        
    else % for one source neuron
        % get all successor nodes for this source neuron (direct
        %  targets)
        thisSuccName = successors(connGraph,sourceNeurons);

        % compare this list of successor nodes to list of targetNeurons
        if ~isempty(thisSuccName)
            thisNumPostNeurons = 0;
            for j = 1:length(thisSuccName)   
                % if this successor node is a targetNeuron, increment
                if any(strcmpi(thisSuccName{j},targetNeurons))
                    thisNumPostNeurons = thisNumPostNeurons + 1;
                end
            end
               
            % update logical if meet threshold
            if (thisNumPostNeurons >= minNumTargets)
                isPreSynLog = true;
            else
                isPreSynLog = false;
            end

            % update num connections
            numTargetsConn = thisNumPostNeurons;
        end
    end
end