% readPostsynConnFromCSV.m
%
% Function that reads in connectivity from folder of CSV files, where each
%  CSV file is a neuron's postsynaptic targets (ID and number of synapses
%  it receives). Each CSV file is named the ID of the presynaptic neuron.
% Returns the connectivity of all the neurons in the CSV file as a set of
%  source, target, names, and weights arrays that can be fed into digraph.
%
% INPUTS:
%   csvFolderPath - full path to folder of CSV files
%
% OUTPUTS:
%   s - cell array of source names (i.e. presynaptic neurons)
%   t - cell array of target names (i.e. postsynaptic neurons; indices
%       matched to those of s; s(1)->t(1), etc.)
%   names - cell array of all names (i.e. neuron IDs)
%   weights - array of connection weights, as number of synapses indices 
%       matched to s and t; weight(1) is number of synapses s(1)->t(1)
%
% CREATED: 12/23/22 - HHY
%
% UPDATED:
%   12/23/22 - HHY
%
function [s, t, names, weights] = readPostsynConnFromCSV(csvFolderPath)

    % get all csv files
    csvFileList = dir([csvFolderPath filesep '6*.csv']);
    
    % initialize
    names = {};
    s = {};
    t = {};
    weights = [];
    
    % loop through all csv files
    for i = 1:length(csvFileList)
        % full path for this CSV file
        thisCSVpath = [csvFolderPath filesep csvFileList(i).name];
        
        % name of this presynaptic neuron
        presynName = csvFileList(i).name;
        presynName = presynName(1:(end-4));
        
        % read csv file
        csvFileContents = readmatrix(thisCSVpath, 'NumHeaderLines', 1, ...
            'Delimiter', ',', 'OutputType', 'char');
        
        % if csv file is empty, reads in header line anyway as only output
        if (~strcmp(csvFileContents(2),'post_id'))
            thisNames = csvFileContents(:,2);
            thisWeights = str2double(csvFileContents(:,3));
            
        else
            thisNames = {};
            thisWeights = [];
        end
        
        % update names, s, t cell arrays with info from this CSV file
        if (~isempty(thisNames))
            % repeat presynaptic name as start node
            presynS = repmat({presynName},length(thisNames),1);
            % add to s
            s = [s; presynS];
            
            % target nodes are list in thisNames
            t = [t; thisNames];
            
            % weights
            weights = [weights; thisWeights];
            
            % update names cell array (will add duplicates, remove later)
            % add presyn name
            names = [names; presynName];
            % add postsyn names
            names = [names; thisNames];
        end
    end
    
    % unique elements only for name
    names = unique(names);
end