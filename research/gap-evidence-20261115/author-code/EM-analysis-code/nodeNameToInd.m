% nodeNameToInd.m
%
% Helper function that takes in name of node (or cell array of nodes) and 
%  returns the index value(s) in full node array. NaN if it can't find node
%  name.
%
% INPUTS:
%   selectNames - names of selected nodes, for which indices are desired,
%       as cell array or single string
%   names - full cell array of node names
%
% OUTPUTS:
%   selectInd - indices of selected names
%
% CREATED: 3/1/23 - HHY
%
% UPDATED:
%   3/1/23 - HHY
%
function selectInd = nodeNameToInd(selectNames, names)

    % if multiple names
    if iscell(selectNames)
        % preallocate
        selectInd = nan(size(selectNames));

        for i = 1:length(selectNames)
            % get index
            thisInd = find(strcmpi(selectNames{i}, names));

            % make sure name actually exists in name array
            if ~isempty(thisInd)
                selectInd(i) = thisInd;
            end
        end
    % if one name (handled differently than cell array)  
    else
        % get index
        thisInd = find(strcmpi(selectNames, names));

        % make sure name actually exists, otherwise, return NaN
        if ~isempty(thisInd)
            selectInd = thisInd;
        else
            selectInd = nan;
        end
    end
end