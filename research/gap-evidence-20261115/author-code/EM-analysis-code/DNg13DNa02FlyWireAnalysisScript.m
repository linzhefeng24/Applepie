% DNg13DNa02FlyWireAnalysisScript.m
%
% Script for performing analyses on DNg13 and DNa02 connectivity in FlyWire
% Based on DNg13DNa02FancAnalysisScript.m
%
% Digraph properties:
%   Nodes:
%     Name - [required by digraph]
%     Whimsy   
%     Neurotransmitter
%  Edges:
%     EndNodes - [required by digraph]
%     NumSyn
%     Neurotransmitter
%
% Last updated: 9/7/23

%% where to save data
saveDataPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/FlyWireConnSummary_230907';

%% load in data, from scratch

% path to CSV files of connectivity, generated from genPresynCSVsFlyWire.r
% csvPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/FlyWirePresynCSVs/230208_3';
csvPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/FlyWirePresynCSVs/230903';

% load in connectivity - get s, t, names, weights to be used in generating
%  digraph
[s, t, names, weights] = readPresynConnFromCSV(csvPath);

% save data
savePath = [saveDataPath filesep 'csvVars.mat'];
save(savePath, 's', 't', 'names', 'weights', '-v7.3');

%% load in data from saved file

csvVarsMatPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/FlyWireConnSummary_230907/csvVars.mat';

load(csvVarsMatPath, 's', 't', 'names', 'weights');

%% match names to whimsy names for DNs

whimsy= repmat({''},size(names));

% IDs from 3/1/23
% dna02L = '720575940604737708';
% dna02R = '720575940629327659';
% dng13L = '720575940633270497';
% dng13R = '720575940616471052';

% IDs from 9/3/23
dna02L = '720575940604737708';
dna02R = '720575940629327659';
dng13L = '720575940606112940';
dng13R = '720575940616471052';


whimsy{strcmp(dna02L,names)} = 'DNa02L';
whimsy{strcmp(dna02R,names)} = 'DNa02R';
whimsy{strcmp(dng13L,names)} = 'DNg13L';
whimsy{strcmp(dng13R,names)} = 'DNg13R';

%% get neurotransmitters

% path to txt files of neurotransmitters, generated from getNTpredFlywire.r
ntFolder = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/FlyWirePresynCSVs/230903_nt';

[ntEdges, neurotransNodes, ntprctNodes] = getNTArrays(ntFolder, s, names);

%% save data: s, t, names, weights, NT, whimsy

savePath = [saveDataPath filesep 'allVars.mat'];
save(savePath, 's', 't', 'names', 'weights', 'whimsy', 'ntEdges', ...
    'neurotransNodes', 'ntprctNodes', '-v7.3');

%% load in data from save file

allVarsMatPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/FlyWireConnSummary_230907/allVars.mat';

load(allVarsMatPath,'s', 't', 'names', 'weights', 'whimsy', 'ntEdges', ...
    'neurotransNodes', 'ntprctNodes');


%% filter by minimum synaptic number

minSynNum = 10;

[sFilt, tFilt, weightsFilt, namesFilt, edgesRmInd, namesRmInd] = ...
    filtDigraphBySynNum(s, t, weights, names, minSynNum);

% update other graph features with same filtering
whimsyFilt = whimsy;
whimsyFilt(namesRmInd) = [];

ntNodesFilt = neurotransNodes;
ntNodesFilt(namesRmInd) = [];

ntprctNodesFilt = ntprctNodes;
ntprctNodesFilt(namesRmInd) = [];

ntEdgesFilt = ntEdges;
ntEdgesFilt(edgesRmInd) = [];


%% generate digraph from s, t, names, weights variables generated from CSVs
% includes normalized weights and neurotransmitters

EdgeTable = table([sFilt tFilt], weightsFilt, ntEdgesFilt, ...
    'VariableNames',{'EndNodes' 'NumSyn' 'Neurotransmitter'});

NodeTable = table(namesFilt, whimsyFilt, ntNodesFilt, ntprctNodesFilt, ...
    'VariableNames',...
    {'Name' 'Whimsy' 'Neurotransmitter' 'NTPercent'});

connGraphAll = digraph(EdgeTable,NodeTable);

%% save data: filtered data + digraph
filtVarsMatPath = [saveDataPath filesep 'filtVars' ...
    num2str(minSynNum) '.mat'];

save(filtVarsMatPath, 'sFilt', 'tFilt', 'weightsFilt', 'namesFilt', ...
    'whimsyFilt','ntNodesFilt', 'ntprctNodesFilt', 'ntEdgesFilt', ...
    'connGraphAll', '-v7.3');

%% load in saved data

filtVarsMatPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/Brain/FlyWireConnSummary/filtVars15.mat';
load(filtVarsMatPath, 'sFilt', 'tFilt', 'weightsFilt', 'namesFilt', ...
    'whimsyFilt','ntNodesFilt', 'ntprctNodesFilt', 'ntEdgesFilt', ...
    'connGraphAll');

%% monosynaptic nodes shared between DNg13 and DNa02 

% a02 monosynaptic presynaptic neurons
a02lMonoSynNodes = nearest(connGraphAll,dna02L,1,'Method','unweighted',...
    'Direction','incoming');
a02rMonoSynNodes = nearest(connGraphAll,dna02R,1,'Method','unweighted',...
    'Direction','incoming');

% g13 monosynaptic presynaptic neurons
g13lMonoSynNodes = nearest(connGraphAll,dng13L,1,'Method','unweighted',...
    'Direction','incoming');
g13rMonoSynNodes = nearest(connGraphAll,dng13R,1,'Method','unweighted',...
    'Direction','incoming');

% ipsilateral monosynaptic presynaptic neurons shared b/w DNa02 and DNg13
a02lg13lMonoSynShared = intersect(a02lMonoSynNodes,g13lMonoSynNodes);
a02rg13rMonoSynShared = intersect(a02rMonoSynNodes,g13rMonoSynNodes);

% monosynaptic presynaptic neurons shared contralateral, same cell type
a02la02rMonoSynShared = intersect(a02lMonoSynNodes, a02rMonoSynNodes);
g13lg13rMonoSynShared = intersect(g13lMonoSynNodes, g13rMonoSynNodes);

%% get some features of monosynaptic nodes
% neurotransmitter, how many synapses they make onto DNs

% DNa02 left
% number of synapses
a02lMonoNumSyn = getNumPreSyn(a02lMonoSynNodes, dna02L, connGraphAll);
% sort so greatest number of synapses is first
[a02lMonoNumSynSort, sortOrder] = sort(a02lMonoNumSyn, 'descend');
% reorder node names by num synapses
a02lMonoSynNodesSort = a02lMonoSynNodes(sortOrder);
% get neurotransmitters
selectInd = nodeNameToInd(a02lMonoSynNodes, namesFilt);
a02lMonoNT = ntNodesFilt(selectInd);
a02lMonoNTSort = a02lMonoNT(sortOrder);
% get neurotransmitter confidence
a02lMonoNTprct = ntprctNodesFilt(selectInd);
a02lMonoNTprctSort = a02lMonoNTprct(sortOrder);
% write to CSV
a02lMonoTable = cell2table([a02lMonoSynNodesSort ...
    num2cell(a02lMonoNumSynSort) a02lMonoNTSort ...
    num2cell(a02lMonoNTprctSort)], ...
    'VariableNames',{'Neurons','NumSyn','Neurotransmitter', 'NTPrct'});
csvFileName = [saveDataPath filesep 'dna02LMonoSyn.csv'];
writetable(a02lMonoTable,csvFileName);


% DNa02 right
% number of synapses
a02rMonoNumSyn = getNumPreSyn(a02rMonoSynNodes, dna02R, connGraphAll);
% sort so greatest number of synapses is first
[a02rMonoNumSynSort, sortOrder] = sort(a02rMonoNumSyn, 'descend');
% reorder node names by num synapses
a02rMonoSynNodesSort = a02rMonoSynNodes(sortOrder);
% get neurotransmitters
selectInd = nodeNameToInd(a02rMonoSynNodes, namesFilt);
a02rMonoNT = ntNodesFilt(selectInd);
a02rMonoNTSort = a02rMonoNT(sortOrder);
% get neurotransmitter confidence
a02rMonoNTprct = ntprctNodesFilt(selectInd);
a02rMonoNTprctSort = a02rMonoNTprct(sortOrder);
% write to CSV
a02rMonoTable = cell2table([a02rMonoSynNodesSort ...
    num2cell(a02rMonoNumSynSort) a02rMonoNTSort ...
    num2cell(a02rMonoNTprctSort)], ...
    'VariableNames',{'Neurons','NumSyn','Neurotransmitter', 'NTPrct'});
csvFileName = [saveDataPath filesep 'dna02RMonoSyn.csv'];
writetable(a02rMonoTable,csvFileName);

% DNg13 left
% number of synapses
g13lMonoNumSyn = getNumPreSyn(g13lMonoSynNodes, dng13L, connGraphAll);
% sort so greatest number of synapses is first
[g13lMonoNumSynSort, sortOrder] = sort(g13lMonoNumSyn, 'descend');
% reorder node names by num synapses
g13lMonoSynNodesSort = g13lMonoSynNodes(sortOrder);
% get neurotransmitters
selectInd = nodeNameToInd(g13lMonoSynNodes, namesFilt);
g13lMonoNT = ntNodesFilt(selectInd);
g13lMonoNTSort = g13lMonoNT(sortOrder);
% get neurotransmitter confidence
g13lMonoNTprct = ntprctNodesFilt(selectInd);
g13lMonoNTprctSort = g13lMonoNTprct(sortOrder);
% write to CSV
g13lMonoTable = cell2table([g13lMonoSynNodesSort ...
    num2cell(g13lMonoNumSynSort) g13lMonoNTSort ...
    num2cell(g13lMonoNTprctSort)], ...
    'VariableNames',{'Neurons','NumSyn','Neurotransmitter', 'NTPrct'});
csvFileName = [saveDataPath filesep 'dng13LMonoSyn.csv'];
writetable(g13lMonoTable,csvFileName);

% DNg13 right
% number of synapses
g13rMonoNumSyn = getNumPreSyn(g13rMonoSynNodes, dng13R, connGraphAll);
% sort so greatest number of synapses is first
[g13rMonoNumSynSort, sortOrder] = sort(g13rMonoNumSyn, 'descend');
% reorder node names by num synapses
g13rMonoSynNodesSort = g13rMonoSynNodes(sortOrder);
% get neurotransmitters
selectInd = nodeNameToInd(g13rMonoSynNodes, namesFilt);
g13rMonoNT = ntNodesFilt(selectInd);
g13rMonoNTSort = g13rMonoNT(sortOrder);
% get neurotransmitter confidence
g13rMonoNTprct = ntprctNodesFilt(selectInd);
g13rMonoNTprctSort = g13rMonoNTprct(sortOrder);
% write to CSV
g13rMonoTable = cell2table([g13rMonoSynNodesSort ...
    num2cell(g13rMonoNumSynSort) g13rMonoNTSort ...
    num2cell(g13rMonoNTprctSort)], ...
    'VariableNames',{'Neurons','NumSyn','Neurotransmitter', 'NTPrct'});
csvFileName = [saveDataPath filesep 'dng13RMonoSyn.csv'];
writetable(g13rMonoTable,csvFileName);


% monosynaptic shared DNa02 and DNg13 left
a02lMonoShareg13lNumSyn = getNumPreSyn(a02lg13lMonoSynShared, dna02L, ...
    connGraphAll);
g13lMonoSharea02lNumSyn = getNumPreSyn(a02lg13lMonoSynShared, dng13L, ...
    connGraphAll);
% get neurotransmitters
selectInd = nodeNameToInd(a02lg13lMonoSynShared, namesFilt);
a02lg13lMonoShareNT = ntNodesFilt(selectInd);
% neurotransmitter confidence
a02lg13lMonoShareNTprct = ntprctNodesFilt(selectInd);
% write to CSV
a02lg13lMonoShareTable = cell2table([a02lg13lMonoSynShared ...
    num2cell(a02lMonoShareg13lNumSyn) num2cell(g13lMonoSharea02lNumSyn) ...
    a02lg13lMonoShareNT num2cell(a02lg13lMonoShareNTprct)],...
    'VariableNames',{'Neurons', 'NumSynDNa02L', 'NumSynDNg13L', ...
    'Neurotransmitter', 'NTPrct'});
csvFileName = [saveDataPath filesep 'a02lg13lMonoSynShared.csv'];
writetable(a02lg13lMonoShareTable,csvFileName);

% monosynaptic shared DNa02 and DNg13 right
a02rMonoShareg13rNumSyn = getNumPreSyn(a02rg13rMonoSynShared, dna02R, ...
    connGraphAll);
g13rMonoSharea02rNumSyn = getNumPreSyn(a02rg13rMonoSynShared, dng13R, ...
    connGraphAll);
% get neurotransmitters
selectInd = nodeNameToInd(a02rg13rMonoSynShared, namesFilt);
a02rg13rMonoShareNT = ntNodesFilt(selectInd);
% neurotransmitter confidence
a02rg13rMonoShareNTprct = ntprctNodesFilt(selectInd);
% write to CSV
a02rg13rMonoShareTable = cell2table([a02rg13rMonoSynShared ...
    num2cell(a02rMonoShareg13rNumSyn) num2cell(g13rMonoSharea02rNumSyn) ...
    a02rg13rMonoShareNT num2cell(a02rg13rMonoShareNTprct)],...
    'VariableNames',{'Neurons', 'NumSynDNa02R', 'NumSynDNg13R', ...
    'Neurotransmitter', 'NTPrct'});
csvFileName = [saveDataPath filesep 'a02rg13rMonoSynShared.csv'];
writetable(a02rg13rMonoShareTable,csvFileName);


%% disynaptic nodes shared between DNg13 and DNa02

a02DiSynNodes = nearest(connGraphAll,dna02,2,'Method','unweighted', ...
    'Direction', 'outgoing');
g13DiSynNodes = nearest(connGraphAll,dng13,2,'Method','unweighted', ...
    'Direction', 'outgoing');

diSynNodes = unique([a02DiSynNodes; g13DiSynNodes; {dna02}; {dng13}]);

%% stacked barplots for categories of monosynaptic inputs
% Note, here, just entering the numbers manually for plotting, from the
%  google spreadsheets. Easier but could write code to automatically read
%  those spreadsheets

% category names
inCatNames = {'motor', 'DN', 'AN', 'visual', 'superior brain'};

% counts for each category, indices match inCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [41; 5; 0; 4; 0];
dna02r_monoCat = [38; 5; 1; 6; 0];

dng13l_monoCat = [35; 10; 2; 1; 2];
dng13r_monoCat = [33; 8; 2; 3; 4];

allDNs_monoCat = [dna02l_monoCat, dna02r_monoCat, ...
    dng13l_monoCat, dng13r_monoCat];

% names for DNs - this flips to account for brain flip
DNnames = {'DNa02 right', 'DNa02 left', 'DNg13 right', 'DNg13 left'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(inCatNames);

ylabel('Number of neurons');

%% cosine similiarity for monosynaptic inputs 

% get all monosynaptic nodes for 4 DNs
% both DNa02
a02lrMonoSynUnion = union(a02lMonoSynNodes, a02rMonoSynNodes);
% both DNg13
g13lrMonoSynUnion = union(g13lMonoSynNodes, g13rMonoSynNodes);
% DNa02 and DNg13
a02lrg13lrMonoSynUnion = union(a02lrMonoSynUnion, g13lrMonoSynUnion);

% get number of synapses made by all of the monosynaptic nodes onto each of
%  the DNs
monoSynAllNumSyn = zeros(4,size(a02lrg13lrMonoSynUnion,1));
monoSynAllNumSyn(1,:) = ...
    getNumPreSyn(a02lrg13lrMonoSynUnion, dna02L, connGraphAll);
monoSynAllNumSyn(2,:) = ...
    getNumPreSyn(a02lrg13lrMonoSynUnion, dna02R, connGraphAll);
monoSynAllNumSyn(3,:) = ...
    getNumPreSyn(a02lrg13lrMonoSynUnion, dng13L, connGraphAll);
monoSynAllNumSyn(4,:) = ...
    getNumPreSyn(a02lrg13lrMonoSynUnion, dng13R, connGraphAll);

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





