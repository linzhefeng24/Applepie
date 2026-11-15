% getNTLinLoc.m
%
% Function to generate digraph arrays for neurons' hemilineage, location,
%  and neurotransmitter (info for both nodes and edges)
%
% INPUTS:
%   ntCSVfile - full path to neurotransmitter CSV file
%   s - array of source nodes for digraph
%   names - array of node names for digraph
%
% OUTPUTS:
%   signEdges - sign of edges connecting source and targets. NaN when
%       unknown, +1 for ACh, -1 for GABA and Glu
%   ntEdges - neurotransmitter for each edge; empty array if unknown
%   hemilinNodes - hemilineage for each node; empty if unknown
%   neurotransNodes - neurotransmitter for each node; empty if unknown
%   locNodes - location for each node (T1-3 and LHS or RHS); empty if
%       unknown
%
% CREATED: 1/3/22 - HHY
%
% UPDATED:
%   1/3/22 - HHY
%
function [signEdges, ntEdges, hemilinNodes, neurotransNodes, locNodes] = ...
    getNTLinLoc(ntCSVfile, s, names)


    ntCSVFileContents = readmatrix(ntCSVfile, 'NumHeaderLines', 1, ...
            'Delimiter', ',', 'OutputType', 'char');
    
    ntNames = ntCSVFileContents(:,1);
    ntLocation = ntCSVFileContents(:,2);
    ntHemilineage = ntCSVFileContents(:,3);
    ntNeurotrans = ntCSVFileContents(:,4);
    
    % get whether excitatory or inhibitory from neurotransmitter
    ntSign = zeros(size(ntNeurotrans));
    for i = 1:length(ntSign)
        if (contains(ntNeurotrans{i},'GABA'))
            ntSign(i) = -1;
        elseif (contains(ntNeurotrans{i},'Glu'))
            % motor neurons shouldn't make synapses
            if ~(any(contains(ntHemilineage{i}, {'15B','24B','21B','20/22B'})))
                ntSign(i) = -1;
            else
                ntSign(i) = nan;
            end
        elseif (strcmpi(ntNeurotrans{i},'ACh'))
            ntSign(i) = 1;
        else
            ntSign(i) = nan;
        end
    end
    
    % get sign and neurotransmitter of edges, for neurons in graph
    signEdges = nan(size(s));
    ntEdges = cell(size(s));
    
    for i = 1:length(signEdges)
        % check to see if start node is one of the ones we have
        %  neurotransmitter info for
    
        thisName = s{i};
    
        % if in the list
        if (any(strcmp(thisName, ntNames)))
            % get index
            ntInd = find(strcmpi(thisName, ntNames));
            thisNt = ntNeurotrans{ntInd};
            thisSign = ntSign(ntInd);
    
            % update signEdges, ntEdges
            signEdges(i) = thisSign;
            ntEdges{i} = thisNt;
        end
    end
    
    % get location, hemilineage, neurotransmitter for neurons in graph
    % to update nodes
    hemilinNodes = repmat({''},size(names));
    neurotransNodes = repmat({''},size(names));
    locNodes = repmat({''},size(names));
    
    % loop through all names, assign location, hemilineage, neurotransmitter
    % when known
    for i = 1:length(hemilinNodes)
        thisName = names{i};
    
        % if name is in list
        if (any(strcmp(thisName, ntNames)))
            % get index
            ntInd = find(strcmpi(thisName,ntNames));
            thisNt = ntNeurotrans{ntInd};
            thisLoc = ntLocation{ntInd};
            thisHemilin = ntHemilineage{ntInd};
    
            % update 
            hemilinNodes{i} = thisHemilin;
            neurotransNodes{i} = thisNt;
            locNodes{i} = thisLoc;
        end 
    end
end