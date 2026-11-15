% braincircuitsIO_DNa02DNg13_inputs.m
%
% Script for reading in spreadsheets of DNa02 and DNg13 brain inputs (from
%  edited version of braincircuits.io output, with column listing category)
% Returns number of shared inputs for cells on left and right side
% Plots bar plots of categories of inputs, both as number of cells and as
%  percent of input neurons
%
% CREATED: 9/28/23 - HHY
%
% UPDATED: 
%   9/28/23 - HHY
%

%% load in spreadsheets
dna02lcsvPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/braincircuitsIO/DNa02L_preT10cat.csv';
dna02lCSV = readmatrix(dna02lcsvPath, 'NumHeaderLines', 1, ...
    'Delimiter', ',', 'OutputType', 'char');
dna02lNames = dna02lCSV(:,1);
dna02lNumSyn = str2double(dna02lCSV(:,2));
dna02lcat = dna02lCSV(:,15);


dna02rcsvPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/braincircuitsIO/DNa02R_preT10cat.csv';
dna02rCSV = readmatrix(dna02rcsvPath, 'NumHeaderLines', 1, ...
    'Delimiter', ',', 'OutputType', 'char');
dna02rNames = dna02rCSV(:,1);
dna02rNumSyn = str2double(dna02rCSV(:,2));
dna02rcat = dna02rCSV(:,15);

dng13lcsvPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/braincircuitsIO/DNg13L_preT10cat.csv';
dng13lCSV = readmatrix(dng13lcsvPath, 'NumHeaderLines', 1, ...
    'Delimiter', ',', 'OutputType', 'char');
dng13lNames = dng13lCSV(:,1);
dng13lNumSyn = str2double(dng13lCSV(:,2));
dng13lcat = dng13lCSV(:,15);

dng13rcsvPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/braincircuitsIO/DNg13R_preT10cat.csv';
dng13rCSV = readmatrix(dng13rcsvPath, 'NumHeaderLines', 1, ...
    'Delimiter', ',', 'OutputType', 'char');
dng13rNames = dng13rCSV(:,1);
dng13rNumSyn = str2double(dng13rCSV(:,2));
dng13rcat = dng13rCSV(:,15);


%% get shared inputs - synapse counts
dna02dng13Lshared = intersect(dna02lNames, dng13lNames);
dna02dng13Rshared = intersect(dna02rNames, dng13rNames);

sharedLDNa02syn = [];
sharedLDNg13syn = [];
for i = 1:length(dna02dng13Lshared)
    sharedLDNa02syn(i) = dna02lNumSyn(strcmpi(dna02dng13Lshared{i},dna02lNames));
    sharedLDNg13syn(i) = dng13lNumSyn(strcmpi(dna02dng13Lshared{i},dng13lNames));
end

sharedRDNa02syn = [];
sharedRDNg13syn = [];
for i = 1:length(dna02dng13Rshared)
    sharedRDNa02syn(i) = dna02rNumSyn(strcmpi(dna02dng13Rshared{i},dna02rNames));
    sharedRDNg13syn(i) = dng13rNumSyn(strcmpi(dna02dng13Rshared{i},dng13rNames));
end


% print some numbers to screen (accounts for flip)
fprintf('DNa02 left num syn: %d\n', sum(dna02rNumSyn));
fprintf('DNg13 left num syn: %d\n', sum(dng13rNumSyn));
fprintf('DNa02 left num syn shared: %d\n', sum(sharedRDNa02syn));
fprintf('DNg13 left num syn shared: %d\n', sum(sharedRDNg13syn));

% print some numbers to screen (accounts for flip)
fprintf('DNa02 right num syn: %d\n', sum(dna02lNumSyn));
fprintf('DNg13 right num syn: %d\n', sum(dng13lNumSyn));
fprintf('DNa02 right num syn shared: %d\n', sum(sharedLDNa02syn));
fprintf('DNg13 right num syn shared: %d\n', sum(sharedLDNg13syn));

%% get shared inputs
dna02dng13Lshared = intersect(dna02lNames, dng13lNames);
dna02dng13Rshared = intersect(dna02rNames, dng13rNames);

% print some numbers to screen (accounts for flip)
fprintf('DNa02 left num inputs: %d\n', length(dna02rNames));
fprintf('DNg13 left num inputs: %d\n', length(dng13rNames));
fprintf('DNa02 and DNg13 left num shared inputs: %d\n', ...
    length(dna02dng13Rshared));

% print some numbers to screen (accounts for flip)
fprintf('DNa02 right num inputs: %d\n', length(dna02lNames));
fprintf('DNg13 right num inputs: %d\n', length(dng13lNames));
fprintf('DNa02 and DNg13 right num shared inputs: %d\n', ...
    length(dna02dng13Lshared));

%% get bar plots for categories of input neurons

% category names
inCatNames = {'motor', 'DN', 'AN', 'visual', 'superior brain', 'CX'};

dna02l_monoCat = zeros(length(inCatNames),1);
dna02r_monoCat =  zeros(length(inCatNames),1);

dng13l_monoCat = zeros(length(inCatNames),1);
dng13r_monoCat = zeros(length(inCatNames),1);

% loop through all categories, get counts
for i = 1:length(inCatNames)
    dna02l_monoCat(i) = sum(strcmpi(dna02lcat,inCatNames{i}));
    dna02r_monoCat(i) = sum(strcmpi(dna02rcat, inCatNames{i}));

    dng13l_monoCat(i) = sum(strcmpi(dng13lcat, inCatNames{i}));
    dng13r_monoCat(i) = sum(strcmpi(dng13rcat, inCatNames{i}));
end

allDNs_monoCat = [dna02l_monoCat, dna02r_monoCat, ...
    dng13l_monoCat, dng13r_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dna02r_monoCat/sum(dna02r_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat),...
    dng13r_monoCat/sum(dng13r_monoCat)] * 100;

% names for DNs - this flips to account for brain flip
DNnames = {'DNa02 right', 'DNa02 left', 'DNg13 right', 'DNg13 left'};

% plot stacked bar plot - neuron counts
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(inCatNames);

ylabel('Number of neurons');

% plot stacked bar plot - normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(inCatNames);

ylabel('Percent of neurons');

%% get bar plots for categories of input neurons - by synapse count

% category names
inCatNames = {'CX', 'superior brain', 'visual', 'AN', 'DN', 'motor'};

dna02l_monoCat = zeros(length(inCatNames),1);
dna02r_monoCat =  zeros(length(inCatNames),1);

dng13l_monoCat = zeros(length(inCatNames),1);
dng13r_monoCat = zeros(length(inCatNames),1);

% loop through all categories, get counts
for i = 1:length(inCatNames)
    dna02l_monoCat(i) = sum(dna02lNumSyn(strcmpi(dna02lcat,inCatNames{i})));
    dna02r_monoCat(i) = sum(dna02rNumSyn(strcmpi(dna02rcat, inCatNames{i})));

    dng13l_monoCat(i) = sum(dng13lNumSyn(strcmpi(dng13lcat, inCatNames{i})));
    dng13r_monoCat(i) = sum(dng13rNumSyn(strcmpi(dng13rcat, inCatNames{i})));
end

allDNs_monoCat = [dna02l_monoCat, dna02r_monoCat, ...
    dng13l_monoCat, dng13r_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dna02r_monoCat/sum(dna02r_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat),...
    dng13r_monoCat/sum(dng13r_monoCat)] * 100;

% names for DNs - this flips to account for brain flip
DNnames = {'DNa02 right', 'DNa02 left', 'DNg13 right', 'DNg13 left'};

% plot stacked bar plot - neuron counts
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(inCatNames);

ylabel('Number of synapses');

% plot stacked bar plot - normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(inCatNames);

ylabel('Percent of synapses');

%% generate digraph

% generate digraph
targetNames = [repmat({'dna02l'},length(dna02lNames),1); ...
    repmat({'dna02r'},length(dna02rNames),1);...
    repmat({'dng13l'},length(dng13lNames),1); ...
    repmat({'dng13r'},length(dng13rNames),1)];

sourceNames = [dna02lNames; dna02rNames; dng13lNames; dng13rNames];
allNumSyn = [dna02lNumSyn; dna02rNumSyn; dng13lNumSyn; dng13rNumSyn];

allNames = [unique(sourceNames); {'dna02l'}; {'dna02r'}; {'dng13l'}; ...
    {'dng13r'}];
EdgeTable = table([sourceNames targetNames], allNumSyn, ...
    'VariableNames',{'EndNodes' 'NumSyn'});

NodeTable = table(allNames, ...
    'VariableNames',...
    {'Name'});

connGraphAll = digraph(EdgeTable,NodeTable);


%% get cosine similarity

% get number of synapses made by all of the monosynaptic nodes onto each of
%  the DNs
monoSynAllNumSyn = zeros(4,size(allNames,1));
monoSynAllNumSyn(1,:) = ...
    getNumPreSyn(allNames, 'dna02l', connGraphAll);
monoSynAllNumSyn(2,:) = ...
    getNumPreSyn(allNames, 'dna02r', connGraphAll);
monoSynAllNumSyn(3,:) = ...
    getNumPreSyn(allNames, 'dng13l', connGraphAll);
monoSynAllNumSyn(4,:) = ...
    getNumPreSyn(allNames, 'dng13r', connGraphAll);

% names for DNs - this flips to account for brain flip
DNnames = {'DNa02 right', 'DNa02 left', 'DNg13 right', 'DNg13 left'};

% cosine similiarity
monoSynAllCosSim = cosineSimilarity(monoSynAllNumSyn);

% cosine similiarity if we're just considering whether input is shared or
%  not
monoSynAllCosSimBinary = cosineSimilarity(double(monoSynAllNumSyn > 0));

% plot as heatmap
figure;
heatmap(DNnames, DNnames, monoSynAllCosSim);
title('Cosine Similarity - Number of Synapses');

% plot binary cosine similarity
figure;
heatmap(DNnames, DNnames, monoSynAllCosSimBinary);
title('Cosine Similarity - Shared Input Neurons');