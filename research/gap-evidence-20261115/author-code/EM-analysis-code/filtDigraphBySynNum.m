% filtDigraphBySynNum.m
%
% Function to filter digraph by number of synapses. Only keep connections
%  (and corresponding neurons) with greater than or equal to minSynNum
%
% INPUTS:
%   s - source neurons, maps all connections
%   t - target neurons, maps all connections
%   weights - number of synapses for all connections
%   names - IDs for neurons
%   minSynNum - minimum number of neurons in connection
%
% OUTPUTS:
%   sFilt - source neurons, only for connections greater than minSynNum
%   tFilt - target neurons, only for connections greater than minSynNum
%   weightsFilt - number of connections, only for connections greater than minSynNum
%   namesFilt - IDs for all neurons that are still left after filtering
%   edgesRmInd - indices into arrays of edges (same as s, t, weights) to be
%       removed; use for other edge arrays
%   namesRmInd - indices into arrays of names (same as names) to be removed
%
% CREATED: 1/3/22 - HHY
%
% UPDATED:
%   1/3/22 - HHY
%

function [sFilt, tFilt, weightsFilt, namesFilt, edgesRmInd, namesRmInd] = ...
    filtDigraphBySynNum(s, t, weights, names, minSynNum)

    % running list of connections that don't meet min syn count
    edgesRmInd = [];
    
    % get connections that don't meet min syn count
    for i = 1:length(weights)
        % check if too few synapses
        if (weights(i) < minSynNum)
            % index to list of those to remove
            edgesRmInd = [edgesRmInd; i];
        end
    end
    
    % copy s, t, weights
    sFilt = s;
    tFilt = t;
    weightsFilt = weights;
    
    % remove connections with too few synapses
    sFilt(edgesRmInd) = [];
    tFilt(edgesRmInd) = [];
    weightsFilt(edgesRmInd) = [];
    
    % remove names that no longer appear in s or t
    
    % temp concatenation of s and t
    stFilt = [sFilt; tFilt];
    
    % unique names in s and t
    stFiltUnique = unique(stFilt);
    
    namesRmInd = [];
    
    % get indices of names that are not in s or t
    for i = 1:length(names)
        if (~any(strcmp(names{i}, stFiltUnique)))
            namesRmInd = [namesRmInd; i];
        end
    end
    
    % remove these names from names
    namesFilt = names;
    namesFilt(namesRmInd) = [];

end