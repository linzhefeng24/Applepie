% DNg13DNa02FancAnalysisScript.m
%
% Script for performing analyses on DNg13 and DNa02 connectivity in FANC
% Newer version of genDNg13DNa02digraphScript.m
%
% Digraph properties:
%   Nodes:
%     Name - [required by digraph]
%     Whimsy    
%     Location
%     Hemilineage
%     Neurotransmitter
%  Edges:
%     EndNodes - [required by digraph]
%     NumSyn
%     NormWeight
%     Sign
%     Neurotransmitter
% Last updated: 9/7/23 - HHY

%% saved data dir
saveDataPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/VNC/Analysis_230907';

%% load in data, from scratch

% path to CSV files of connectivity, generated from genPostsynCSVsFANC.r
csvPath = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/VNC/PostsynCSVs/230903';

% load in connectivity - get s, t, names, weights to be used in generating
%  digraph
[s, t, names, weights] = readPostsynConnFromCSV(csvPath);

%% save connectivity data
saveConnPath = [saveDataPath filesep 'csvVars.mat'];
save(saveConnPath, 's', 't', 'names', 'weights', '-v7.3');

%% load in data, from previously saved file
csvVarsMatPath = [saveDataPath filesep 'csvVars.mat'];

load(csvVarsMatPath, 's', 't', 'names', 'weights');

%% match names to whimsy names for DNs

whimsy= repmat({''},size(names));

% current as of 9/3/23
dna02 = '648518346478550356';
dng13 = '648518346497743463';
dna01a = '648518346476472438';
dna01b = '648518346475464576';
dna01c = '648518346481256591';
dna01d = '648518346494759562';

whimsy{strcmp(dna02,names)} = 'DNa02';
whimsy{strcmp(dng13,names)} = 'DNg13';
whimsy{strcmp(dna01a, names)} = 'DNa01a';
whimsy{strcmp(dna01b, names)} = 'DNa01b';
whimsy{strcmp(dna01c, names)} = 'DNa01c';
whimsy{strcmp(dna01d, names)} = 'DNa01d';

%% get neurotransmitter info (and location and hemilineage)

% CSV file
ntCSVfile = [saveDataPath filesep 'Neurotransmitter_all_230906.csv'];

[signEdges, ntEdges, hemilinNodes, neurotransNodes, locNodes] = ...
    getNTLinLoc(ntCSVfile, s, names);

%% name all leg motor neurons

% CSV file
allLegMNCSV = [saveDataPath filesep 'all_leg_motor_neuron_table_v0_230907.csv'];

mnCSVFileContents = readmatrix(allLegMNCSV, 'NumHeaderLines', 1, ...
        'Delimiter', ',', 'OutputType', 'char');

% get names and classification
allLegMNnames = mnCSVFileContents(:,7);
allLegMNclass = mnCSVFileContents(:,12);

% preallocate
allLegMNloc = cell(size(allLegMNclass));

% interpret classification into location info
for i = 1:length(allLegMNclass)
    thisClass = allLegMNclass{i};

    % get hemisphere
    if (strcmp(thisClass(end), 'R'))
        thisHemi = 'RHS';
    elseif (strcmpi(thisClass(end),'L'))
        thisHemi = 'LHS';
    end

    % get which neuromere
    thisNeuromere = thisClass((end-2):(end-1));

    allLegMNloc{i} = [thisHemi ' ' thisNeuromere];
end

% update locNodes, neurotrans, generate isLegMN info for nodes
% preallocate
isLegMN = false(size(names));

for i = 1:length(allLegMNnames)

    % see if this MN is part of all loaded in neurons
    thisInd = find(strcmp(allLegMNnames{i}, names));

    % if it is, update location, NT info, flip MN flag
    if ~isempty(thisInd)
        locNodes{thisInd} = allLegMNloc{i};
        neurotransNodes{thisInd} = 'Glu';
        isLegMN(thisInd) = true;
    end

    % check if this MN makes any output synapses (if yes, error)
    % remove those edges
    thisMNEdgeInd = find(strcmp(allLegMNnames{i}, s));

    if ~isempty(thisMNEdgeInd)
        s(thisMNEdgeInd) = [];
        t(thisMNEdgeInd) = [];
        weights(thisMNEdgeInd) = [];
%             normWeightsFilt(thisMNEdgeInd) = [];
        signEdges(thisMNEdgeInd) = [];
        ntEdges(thisMNEdgeInd) = [];
    end
end


%% get normalized weights
% synNumCSVFile = '/Users/hyang/Dropbox (Personal)/Wilson Lab/EM reconstruction/VNC/a02g13_221219_t10_synNum.csv';
% 
% normWeights = getNormSynWeight(synNumCSVFile, t, weights);


%% filter by minimum synaptic number

minSynNum = 15;

[sFilt, tFilt, weightsFilt, namesFilt, edgesRmInd, namesRmInd] = ...
    filtDigraphBySynNum(s, t, weights, names, minSynNum);

% remove nodes from whimsy, hemilin, neurotrans, location, isMN
whimsyFilt = whimsy;
whimsyFilt(namesRmInd) = [];

hemilinNodesFilt = hemilinNodes;
hemilinNodesFilt(namesRmInd) = [];

neurotransNodesFilt = neurotransNodes;
neurotransNodesFilt(namesRmInd) = [];

locNodesFilt = locNodes;
locNodesFilt(namesRmInd) = [];

isLegMNFilt = isLegMN;
isLegMNFilt(namesRmInd) = [];

% remove edges from normWeights, signEdges, ntEdges
% normWeightsFilt = normWeights;
% normWeightsFilt(edgesRmInd) = [];

signEdgesFilt = signEdges;
signEdgesFilt(edgesRmInd) = [];

ntEdgesFilt = ntEdges;
ntEdgesFilt(edgesRmInd) = [];

%% get T1 MN info

% T1 motor neurons, with identities
t1MNfile = [saveDataPath filesep 'motor_neuron_table_v7_extended_230906.csv'];

t1mnCSVFileContents = readmatrix(t1MNfile, 'NumHeaderLines', 1, ...
        'Delimiter', ',', 'OutputType', 'char');

t1MNnames = t1mnCSVFileContents(:,6);
t1MNCellType = t1mnCSVFileContents(:,4);
t1MNLocs = t1mnCSVFileContents(:,3);
t1MNJoint = t1mnCSVFileContents(:,8);
t1MNSwSt = t1mnCSVFileContents(:,9);
t1MNMuscle = t1mnCSVFileContents(:,10);
t1MNAction = t1mnCSVFileContents(:,11);

% update node info
jointFilt = repmat({''},size(whimsyFilt));
swStFilt = repmat({''},size(whimsyFilt));
muscleFilt = repmat({''},size(whimsyFilt));
actionFilt = repmat({''},size(whimsyFilt));

a02g13T1MNnames = {};

% loop through all T1 motor neurons
for i = 1:length(t1MNnames)

    % if this MN is in node list, update node info
    thisMNind = find(strcmp(t1MNnames{i},namesFilt));

    if ~isempty(thisMNind)
        a02g13T1MNnames = [a02g13T1MNnames; namesFilt{thisMNind}];

        thisCellType = t1MNCellType{i};
        thisCellType(t1MNCellType{i}=='_') = ' ';
        whimsyFilt{thisMNind} = thisCellType;
        
        thisLoc = t1MNLocs{i};
        if (contains(thisLoc, 'T1L'))
            locNodesFilt{thisMNind} = 'LHS T1';
        elseif (contains(thisLoc, 'T1R'))
            locNodesFilt{thisMNind} = 'RHS T1';
        end
        
        jointFilt{thisMNind} = t1MNJoint{i};
        swStFilt{thisMNind} = t1MNSwSt{i};
        muscleFilt{thisMNind} = t1MNMuscle{i};
        actionFilt{thisMNind} = t1MNAction{i};

        % check if this T1 MN makes any output synapses (if yes, error)
        % remove those edges
        thisMNEdgeInd = find(strcmp(t1MNnames{i}, sFilt));

        if ~isempty(thisMNEdgeInd)
            sFilt(thisMNEdgeInd) = [];
            tFilt(thisMNEdgeInd) = [];
            weightsFilt(thisMNEdgeInd) = [];
%             normWeightsFilt(thisMNEdgeInd) = [];
            signEdgesFilt(thisMNEdgeInd) = [];
            ntEdgesFilt(thisMNEdgeInd) = [];
        end
    end
end

%% generate digraph from s, t, names, weights variables generated from CSVs
% includes normalized weights and neurotransmitters

% EdgeTable = table([sFilt tFilt], weightsFilt, normWeightsFilt, ...
%     signEdgesFilt, ntEdgesFilt, ...
%     'VariableNames',{'EndNodes' 'NumSyn' 'NormWeight' 'Sign' 'Neurotransmitter'});

EdgeTable = table([sFilt tFilt], weightsFilt,  ...
    signEdgesFilt, ntEdgesFilt, ...
    'VariableNames',{'EndNodes' 'NumSyn' 'Sign' 'Neurotransmitter'});

NodeTable = table(namesFilt, whimsyFilt, locNodesFilt, hemilinNodesFilt, ...
    isLegMNFilt, neurotransNodesFilt, jointFilt, swStFilt, muscleFilt, ...
    actionFilt, ...
    'VariableNames',...
    {'Name' 'Whimsy' 'Location' 'Hemilineage' 'IsMN', 'Neurotransmitter' ...
    'Joint' 'SwingStance' 'MuscleTarget' 'MotorAction'});

connGraphAll = digraph(EdgeTable,NodeTable);

%% save connectivity graph, specify number of synapses
filtVarsMatPath = [saveDataPath filesep 'filtVars' ...
    num2str(minSynNum) '.mat'];

save(filtVarsMatPath, 'sFilt', 'tFilt', 'weightsFilt', 'signEdgesFilt', ...
    'ntEdgesFilt', 'namesFilt', 'whimsyFilt', 'locNodesFilt', ...
    'hemilinNodesFilt', 'neurotransNodesFilt', 'jointFilt', 'swStFilt', ...
    'muscleFilt', 'actionFilt', 'isLegMNFilt', ...
    'connGraphAll', '-v7.3');

%% nodes shared b/w DNa02 and DNg13 
a02MonoSynNodes = nearest(connGraphAll,dna02,1,'Method','unweighted');
g13MonoSynNodes = nearest(connGraphAll,dng13,1,'Method','unweighted');
a02g13MonoSynShared = intersect(a02MonoSynNodes,g13MonoSynNodes);

a02DiSynNodes = nearest(connGraphAll,dna02,2,'Method','unweighted', ...
    'Direction', 'outgoing');
g13DiSynNodes = nearest(connGraphAll,dng13,2,'Method','unweighted', ...
    'Direction', 'outgoing');

diSynNodes = unique([a02DiSynNodes; g13DiSynNodes; {dna02}; {dng13}]);

%% write CSV files for monosynaptic outputs
% include whether neuron is premotor (specifically, number of MN targets)

% DNa02
% number of synapses
a02MonoNumSyn = getNumPostSyn(dna02, a02MonoSynNodes, connGraphAll);
% sort so greatest number of synapses is first
[a02MonoNumSynSort, sortOrder] = sort(a02MonoNumSyn, 'descend');

% reorder node names by num synapses
a02MonoSynNodesSort = a02MonoSynNodes(sortOrder);

% get location
selectInd = nodeNameToInd(a02MonoSynNodes, namesFilt);

a02MonoLoc = locNodesFilt(selectInd);
a02MonoLocSort = a02MonoLoc(sortOrder);

% get if MN
a02MonoIsMN = isLegMNFilt(selectInd);
a02MonoIsMNSort = a02MonoIsMN(sortOrder);

% get number of leg MN targets
[~, a02NumMNTargets] = isPreSyn(a02MonoSynNodesSort, allLegMNnames, ...
    1, connGraphAll);

% write to CSV
a02MonoTable = cell2table([a02MonoSynNodesSort ...
    num2cell(a02MonoNumSynSort) a02MonoLocSort ...
    num2cell(a02MonoIsMNSort) num2cell(a02NumMNTargets)], ...
    'VariableNames',{'Neurons','NumSyn','Location', 'Is MN?', ...
    'Num MN Targets'});
csvFileName = [saveDataPath filesep 'a02MonoSyn.csv'];
writetable(a02MonoTable,csvFileName);


% DNg13
% number of synapses
g13MonoNumSyn = getNumPostSyn(dng13, g13MonoSynNodes, connGraphAll);
% sort so greatest number of synapses is first
[g13MonoNumSynSort, sortOrder] = sort(g13MonoNumSyn, 'descend');

% reorder node names by num synapses
g13MonoSynNodesSort = g13MonoSynNodes(sortOrder);

% get location
selectInd = nodeNameToInd(g13MonoSynNodes, namesFilt);

g13MonoLoc = locNodesFilt(selectInd);
g13MonoLocSort = g13MonoLoc(sortOrder);

% get if MN
g13MonoIsMN = isLegMNFilt(selectInd);
g13MonoIsMNSort = g13MonoIsMN(sortOrder);

% get number of leg MN targets
[~, g13NumMNTargets] = isPreSyn(g13MonoSynNodesSort, allLegMNnames, ...
    1, connGraphAll);

% write to CSV
g13MonoTable = cell2table([g13MonoSynNodesSort ...
    num2cell(g13MonoNumSynSort) g13MonoLocSort ...
    num2cell(g13MonoIsMNSort) num2cell(g13NumMNTargets)], ...
    'VariableNames',{'Neurons','NumSyn','Location', 'Is MN?', ...
    'Num MN Targets'});
csvFileName = [saveDataPath filesep 'g13MonoSyn.csv'];
writetable(g13MonoTable,csvFileName);



%% stacked barplots for categories of monosynaptic outputs
% Note, here, just entering the numbers manually for plotting, from the
%  google spreadsheets. Easier but could write code to automatically read
%  those spreadsheets

% wing vs. leg circuitry
% category names
outCatNames = {'Leg', 'Wing'};

% counts for each category, indices match outCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [56; 25];

dng13l_monoCat = [67; 0];

allDNs_monoCat = [dna02l_monoCat, dng13l_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat)];

% names for DNs
DNnames = {'DNa02', 'DNg13'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Number of neurons');

% plot stacked bar plot, normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Percent of neurons');


% of leg neurons, categories
% category names
outCatNames = {'MN', 'Local premotor', 'Local', 'Intersegmental', ...
    'Intersegmental premotor', 'AN'};

% counts for each category, indices match outCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [9; 28; 6; 4; 6; 1];

dng13l_monoCat = [2; 39; 10; 5; 9; 2];

allDNs_monoCat = [dna02l_monoCat, dng13l_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat)];

% names for DNs
DNnames = {'DNa02', 'DNg13'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Number of neurons');

% plot stacked bar plot, normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Percent of neurons');


% of leg neurons, categories by neuromere
% category names
outCatNames = {'T1', 'T2', 'T3'};

% counts for each category, indices match outCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [23; 16; 15];

dng13l_monoCat = [30; 21; 16];

allDNs_monoCat = [dna02l_monoCat, dng13l_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat)];

% names for DNs
DNnames = {'DNa02', 'DNg13'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Number of neurons');

% plot stacked bar plot, normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Percent of neurons');


% of wing neurons, categories
% category names
outCatNames = {'Wing MN', 'Haltere MN', 'Neck MN', 'AN', ...
    'Unilateral', 'Bilateral'};

% counts for each category, indices match outCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [5; 2; 1; 6; 2; 9];

dng13l_monoCat = [0; 0; 0; 0; 0; 0];

allDNs_monoCat = [dna02l_monoCat, dng13l_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat)];

% names for DNs
DNnames = {'DNa02', 'DNg13'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Number of neurons');

% plot stacked bar plot, normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Percent of neurons');

%% stacked barplots for categories of monosynaptic outputs - synapse counts
% Note, here, just entering the numbers manually for plotting, from the
%  google spreadsheets. Easier but could write code to automatically read
%  those spreadsheets

% wing vs. leg circuitry
% category names
outCatNames = {'Leg', 'Wing'};

% counts for each category, indices match outCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [1833; 645];

dng13l_monoCat = [2131; 0];

allDNs_monoCat = [dna02l_monoCat, dng13l_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat)];

% names for DNs
DNnames = {'DNa02', 'DNg13'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Number of synapses');

% plot stacked bar plot, normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Percent of synapses');


% of leg neurons, categories
% category names
outCatNames = {'MN', 'Local premotor', 'Local', 'Intersegmental', ...
    'Intersegmental premotor', 'AN'};

% counts for each category, indices match outCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [268; 1244; 95; 74; 154; 18];

dng13l_monoCat = [81; 1233; 470; 73; 248; 26];

allDNs_monoCat = [dna02l_monoCat, dng13l_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat)];

% names for DNs
DNnames = {'DNa02', 'DNg13'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Number of neurons');

% plot stacked bar plot, normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Percent of synapses');


% of leg neurons, categories by neuromere
% category names
outCatNames = {'T1', 'T2', 'T3'};

% counts for each category, indices match outCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [794; 612; 427];

dng13l_monoCat = [800; 903; 428];

allDNs_monoCat = [dna02l_monoCat, dng13l_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat)];

% names for DNs
DNnames = {'DNa02', 'DNg13'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Number of synapses');

% plot stacked bar plot, normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Percent of synapses');


% of wing neurons, categories
% category names
outCatNames = {'Wing MN', 'Haltere MN', 'Neck MN', 'AN', ...
    'Unilateral', 'Bilateral'};

% counts for each category, indices match outCatNames
% DN variable names match spreadsheet names
dna02l_monoCat = [163; 44; 23; 85; 22; 308];

dng13l_monoCat = [0; 0; 0; 0; 0; 0];

allDNs_monoCat = [dna02l_monoCat, dng13l_monoCat];

allDNs_monoCatNorm = [dna02l_monoCat/sum(dna02l_monoCat), ...
    dng13l_monoCat/sum(dng13l_monoCat)];

% names for DNs
DNnames = {'DNa02', 'DNg13'};

% plot stacked bar plot
figure;

bar(allDNs_monoCat', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Number of neurons');

% plot stacked bar plot, normalized
figure;

bar(allDNs_monoCatNorm', 'stacked');

xticklabels(DNnames);

legend(outCatNames);

ylabel('Percent of neurons');

%% get graph only for T1 MN

mnPreNodes = {};
for i = 1:length(a02g13T1MNnames)
    thisMNname = a02g13T1MNnames{i};

    thisMNInputs = nearest(connGraphAll,thisMNname,1,'Method','unweighted', ...
        'Direction', 'incoming');

    mnPreNodes = [mnPreNodes; thisMNInputs];
end

% unique nodes only
mnPreNodesUni = unique(mnPreNodes);

% monosynaptic partners of a02 or g13
a02g13MonoSynNodes = unique([a02MonoSynNodes; g13MonoSynNodes]);

% t1 MN presynaptic neurons that are also a02 or g13 targets
a02g13MonoMNPreNodes = intersect(mnPreNodesUni, a02g13MonoSynNodes);

a02MonoMNPreNodes = intersect(mnPreNodesUni, a02MonoSynNodes);
g13MonoMNPreNodes = intersect(mnPreNodesUni, g13MonoSynNodes);

% t1 MN disynaptic to a02 or g13
a02g13DiSynNodes = unique([a02DiSynNodes; g13DiSynNodes]);
diSynT1MN = intersect(a02g13T1MNnames, a02g13DiSynNodes);

% append DNa02, DNg13, MN themselves
t1MNGraphNodes = unique([a02g13MonoMNPreNodes; dna02; dng13; diSynT1MN]);


t1MNGraph = subgraph(connGraphAll, t1MNGraphNodes);

%% subgraph only DNa02
t1MNa02 = nearest(t1MNGraph, dna02, 2, 'Method','unweighted', ...
        'Direction', 'outgoing');

t1MNa02Graph = subgraph(t1MNGraph, [t1MNa02; dna02]);


%% subgraph only DNg13

t1MNg13 = nearest(t1MNGraph, dng13, 2, 'Method','unweighted', ...
        'Direction', 'outgoing');

t1MNg13Graph = subgraph(t1MNGraph, [t1MNg13; dng13]);

%% only disynaptic connections

% valid start and end nodes: DNa02, DNg13, T1 MNs
valStartEndNodes = [diSynT1MN; dna02; dng13];

% running tracker of edges to remove
allRmInd = []; 

% loop through all edges, check if it's one to remove
% remove if start and end node both aren't MN, DNa02, DNg13
for i = 1:size(t1MNGraph.Edges,1)
    % check start node
    valStart = any(strcmp(t1MNGraph.Edges(i,1).EndNodes{1},valStartEndNodes));

    % check end node
    valEnd = any(strcmp(t1MNGraph.Edges(i,1).EndNodes{2},valStartEndNodes));

    if (~valStart && ~valEnd)
        allRmInd = [allRmInd; i];
    end
end

% remove edges from graph
t1MNGraphDi = rmedge(t1MNGraph,allRmInd);

% new DNa02 and DNg13 subgraphs, disynaptic only
t1MNa02Di = nearest(t1MNGraphDi, dna02, 2, 'Method','unweighted', ...
        'Direction', 'outgoing');
t1MNa02GraphDi = subgraph(t1MNGraphDi, [t1MNa02Di; dna02]);

t1MNg13Di = nearest(t1MNGraphDi, dng13, 2, 'Method','unweighted', ...
        'Direction', 'outgoing');
t1MNg13GraphDi = subgraph(t1MNGraphDi, [t1MNg13Di; dng13]);


%% plot subgraph: motor neurons
lWidths = 10*t1MNGraph.Edges.NumSyn/max(t1MNGraph.Edges.NumSyn);
figure;
% plot(connGraph,'NodeLabel',connGraph.Nodes.Whimsy,'EdgeLabel',...
%     connGraph.Edges.NumSyn, 'LineWidth',lWidths);

h = plot(t1MNGraph,'NodeLabel',t1MNGraph.Nodes.MotorAction, 'LineWidth',lWidths, ...
    'NodeColor', 'k', 'EdgeColor', 'k');

% highlight DNa02 and DNg13 with red nodes, larger
highlight(h, {dna02}, 'NodeColor', 'b', 'MarkerSize', 8);
highlight(h, {dng13}, 'NodeColor', 'r', 'MarkerSize', 8);

% color edges by neurotransmitter
% Ach
achInd = find(strcmpi('ACh', t1MNGraph.Edges.Neurotransmitter));
highlight(h, t1MNGraph.Edges.EndNodes(achInd,1),...
    t1MNGraph.Edges.EndNodes(achInd,2),...
    'EdgeColor','m');
% GABA
gabaInd = find(strcmpi('GABA', t1MNGraph.Edges.Neurotransmitter));
highlight(h, t1MNGraph.Edges.EndNodes(gabaInd,1),...
    t1MNGraph.Edges.EndNodes(gabaInd,2),...
    'EdgeColor','g');
% Glu
gluInd = find(strcmpi('Glu', t1MNGraph.Edges.Neurotransmitter));
highlight(h, t1MNGraph.Edges.EndNodes(gluInd,1),...
    t1MNGraph.Edges.EndNodes(gluInd,2),...
    'EdgeColor','c');

%% plot subgraph: motor neurons a02
lWidths = 10*t1MNa02Graph.Edges.NumSyn/max(t1MNa02Graph.Edges.NumSyn);
figure;
% plot(connGraph,'NodeLabel',connGraph.Nodes.Whimsy,'EdgeLabel',...
%     connGraph.Edges.NumSyn, 'LineWidth',lWidths);

h = plot(t1MNa02Graph ,'NodeLabel',t1MNa02Graph.Nodes.MotorAction, 'LineWidth',lWidths, ...
    'NodeColor', 'k', 'EdgeColor', 'k', 'Layout','layered');

% highlight DNa02 and DNg13 with red nodes, larger
highlight(h, {dna02}, 'NodeColor', 'b', 'MarkerSize', 8);
% highlight(h, {dng13}, 'NodeColor', 'r', 'MarkerSize', 8);

% color edges by neurotransmitter
% Ach
achInd = find(strcmpi('ACh', t1MNa02Graph.Edges.Neurotransmitter));
highlight(h, t1MNa02Graph.Edges.EndNodes(achInd,1),...
    t1MNa02Graph.Edges.EndNodes(achInd,2),...
    'EdgeColor','m');
% GABA
gabaInd = find(strcmpi('GABA', t1MNa02Graph.Edges.Neurotransmitter));
highlight(h, t1MNa02Graph.Edges.EndNodes(gabaInd,1),...
    t1MNa02Graph.Edges.EndNodes(gabaInd,2),...
    'EdgeColor','g');
% Glu
gluInd = find(strcmpi('Glu', t1MNa02Graph.Edges.Neurotransmitter));
highlight(h, t1MNa02Graph.Edges.EndNodes(gluInd,1),...
    t1MNa02Graph.Edges.EndNodes(gluInd,2),...
    'EdgeColor','c');

title('DNa02');

% hide edges more than disynaptic from DNa02


%% plot subgraph: motor neurons g13
lWidths = 10*t1MNg13Graph.Edges.NumSyn/max(t1MNg13Graph.Edges.NumSyn);
figure;
% plot(connGraph,'NodeLabel',connGraph.Nodes.Whimsy,'EdgeLabel',...
%     connGraph.Edges.NumSyn, 'LineWidth',lWidths);

h = plot(t1MNg13Graph,'NodeLabel',t1MNg13Graph.Nodes.MotorAction, 'LineWidth',lWidths, ...
    'NodeColor', 'k', 'EdgeColor', 'k', 'Layout','layered');

% highlight DNa02 and DNg13 with red nodes, larger
% highlight(h, {dna02}, 'NodeColor', 'b', 'MarkerSize', 8);
highlight(h, {dng13}, 'NodeColor', 'b', 'MarkerSize', 8);

% color edges by neurotransmitter
% Ach
achInd = find(strcmpi('ACh', t1MNg13Graph.Edges.Neurotransmitter));
highlight(h, t1MNg13Graph.Edges.EndNodes(achInd,1),...
    t1MNg13Graph.Edges.EndNodes(achInd,2),...
    'EdgeColor','m');
% GABA
gabaInd = find(strcmpi('GABA', t1MNg13Graph.Edges.Neurotransmitter));
highlight(h, t1MNg13Graph.Edges.EndNodes(gabaInd,1),...
    t1MNg13Graph.Edges.EndNodes(gabaInd,2),...
    'EdgeColor','g');
% Glu
gluInd = find(strcmpi('Glu', t1MNg13Graph.Edges.Neurotransmitter));
highlight(h, t1MNg13Graph.Edges.EndNodes(gluInd,1),...
    t1MNg13Graph.Edges.EndNodes(gluInd,2),...
    'EdgeColor','c');

title('DNg13');








%% plot subgraph: motor neurons
% Disynaptic connections to MN only (hide connections b/w local neurons)
lWidths = 10*t1MNGraphDi.Edges.NumSyn/max(t1MNGraphDi.Edges.NumSyn);
figure;
% plot(connGraph,'NodeLabel',connGraph.Nodes.Whimsy,'EdgeLabel',...
%     connGraph.Edges.NumSyn, 'LineWidth',lWidths);

h = plot(t1MNGraphDi,'NodeLabel',t1MNGraphDi.Nodes.MotorAction, 'LineWidth',lWidths, ...
    'NodeColor', 'k', 'EdgeColor', 'k', 'Layout', 'layered');

% highlight DNa02 and DNg13 with red nodes, larger
highlight(h, {dna02}, 'NodeColor', 'b', 'MarkerSize', 8);
highlight(h, {dng13}, 'NodeColor', 'r', 'MarkerSize', 8);

% color edges by neurotransmitter
% Ach
achInd = find(strcmpi('ACh', t1MNGraphDi.Edges.Neurotransmitter));
highlight(h, t1MNGraphDi.Edges.EndNodes(achInd,1),...
    t1MNGraphDi.Edges.EndNodes(achInd,2),...
    'EdgeColor','m');
% GABA
gabaInd = find(strcmpi('GABA', t1MNGraphDi.Edges.Neurotransmitter));
highlight(h, t1MNGraphDi.Edges.EndNodes(gabaInd,1),...
    t1MNGraphDi.Edges.EndNodes(gabaInd,2),...
    'EdgeColor','g');
% Glu
gluInd = find(strcmpi('Glu', t1MNGraphDi.Edges.Neurotransmitter));
highlight(h, t1MNGraphDi.Edges.EndNodes(gluInd,1),...
    t1MNGraphDi.Edges.EndNodes(gluInd,2),...
    'EdgeColor','c');

ttlStr = sprintf('DNa02 and DNg13 with T1 MN, disynaptic only, numSyn >= %d', minSynNum);
title(ttlStr);

%% plot subgraph: motor neurons a02
% Disynaptic connections to MN only (hide connections b/w local neurons)
lWidths = 4*t1MNa02GraphDi.Edges.NumSyn/max(t1MNa02GraphDi.Edges.NumSyn);
figure;
% plot(connGraph,'NodeLabel',connGraph.Nodes.Whimsy,'EdgeLabel',...
%     connGraph.Edges.NumSyn, 'LineWidth',lWidths);

h = plot(t1MNa02GraphDi ,'NodeLabel',t1MNa02GraphDi.Nodes.MotorAction, ...
    'LineWidth',lWidths, ...
    'NodeColor', 'k', 'EdgeColor', 'k', 'Layout','layered');

% highlight DNa02 and DNg13 with red nodes, larger
highlight(h, {dna02}, 'NodeColor', 'b', 'MarkerSize', 8);
% highlight(h, {dng13}, 'NodeColor', 'r', 'MarkerSize', 8);

% color edges by neurotransmitter
% Ach
achInd = find(strcmpi('ACh', t1MNa02GraphDi.Edges.Neurotransmitter));
highlight(h, t1MNa02GraphDi.Edges.EndNodes(achInd,1),...
    t1MNa02GraphDi.Edges.EndNodes(achInd,2),...
    'EdgeColor','m');
% GABA
gabaInd = find(strcmpi('GABA', t1MNa02GraphDi.Edges.Neurotransmitter));
highlight(h, t1MNa02GraphDi.Edges.EndNodes(gabaInd,1),...
    t1MNa02GraphDi.Edges.EndNodes(gabaInd,2),...
    'EdgeColor','g');
% Glu
gluInd = find(strcmpi('Glu', t1MNa02GraphDi.Edges.Neurotransmitter));
highlight(h, t1MNa02GraphDi.Edges.EndNodes(gluInd,1),...
    t1MNa02GraphDi.Edges.EndNodes(gluInd,2),...
    'EdgeColor','c');

ttlStr = sprintf('DNa02 with T1 MN, disynatic only, numSyn >= %d', minSynNum);
title(ttlStr);


%% plot subgraph: motor neurons g13
% Disynaptic connections to MN only (hide connections b/w local neurons)
lWidths = 4*t1MNg13GraphDi.Edges.NumSyn/max(t1MNg13GraphDi.Edges.NumSyn);
figure;
% plot(connGraph,'NodeLabel',connGraph.Nodes.Whimsy,'EdgeLabel',...
%     connGraph.Edges.NumSyn, 'LineWidth',lWidths);

h = plot(t1MNg13GraphDi,'NodeLabel',t1MNg13GraphDi.Nodes.MotorAction, 'LineWidth',lWidths, ...
    'NodeColor', 'k', 'EdgeColor', 'k', 'Layout','layered');

% highlight DNa02 and DNg13 with red nodes, larger
% highlight(h, {dna02}, 'NodeColor', 'b', 'MarkerSize', 8);
highlight(h, {dng13}, 'NodeColor', 'b', 'MarkerSize', 8);

% color edges by neurotransmitter
% Ach
achInd = find(strcmpi('ACh', t1MNg13GraphDi.Edges.Neurotransmitter));
highlight(h, t1MNg13GraphDi.Edges.EndNodes(achInd,1),...
    t1MNg13GraphDi.Edges.EndNodes(achInd,2),...
    'EdgeColor','m');
% GABA
gabaInd = find(strcmpi('GABA', t1MNg13GraphDi.Edges.Neurotransmitter));
highlight(h, t1MNg13GraphDi.Edges.EndNodes(gabaInd,1),...
    t1MNg13GraphDi.Edges.EndNodes(gabaInd,2),...
    'EdgeColor','g');
% Glu
gluInd = find(strcmpi('Glu', t1MNg13GraphDi.Edges.Neurotransmitter));
highlight(h, t1MNg13GraphDi.Edges.EndNodes(gluInd,1),...
    t1MNg13GraphDi.Edges.EndNodes(gluInd,2),...
    'EdgeColor','c');

ttlStr = sprintf('DNg13 with T1 MN, disynatic only, numSyn >= %d', minSynNum);
title(ttlStr);