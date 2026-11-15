% getFANCcontributions.m
%
% Function to read in output of csvFancChangeLog function (in R), to get
%  user contributions to all neurons in specified folder. Each neuron is a 
%  single CSV file
% Returns table of users, user affiliations, user IDs, number of edits,
%  number of neurons
%
% INPUTS:
%   changeLogFolderPath - full path to folder containing output CSVs of
%       csvFancChangeLog()
%
% OUTPUTS:
%   outTable - output table
%
% CREATED: 10/24/23 - HHY
%
% UPDATED:
%   10/24/23 - HHY
%
function outTable = getFANCcontributions(changeLogFolderPath)
    % get all csv files in changeLog folder
    % all IDs start with 6
    allCSVs = dir([changeLogFolderPath filesep '6*.csv']);

    % initialize trackers of all info
    usersAll = {};
%     userAffilAll = {};
    userIDsAll = [];
    whichNeuron = {};

    % loop through all files
    for i = 1:length(allCSVs)
        % get path for this csv
        thisCSVPath = [allCSVs(i).folder filesep allCSVs(i).name];
        % get name for this neuron
        thisNeuronName = allCSVs(i).name(1:(end-4));
        % read in CSV
        thisCSV = readmatrix(thisCSVPath, 'NumHeaderLines', 1, ...
            'Delimiter', ',', 'OutputType', 'char');

        % get info
        if (size(thisCSV,2) > 6)
            thisUserID = str2double(thisCSV(:,3));
            thisUser = thisCSV(:,7);
    %         thisAffil = thisCSV(:,8);
            thisNeuron = repmat({thisNeuronName},length(thisUser),1);
    
            % add to tracker across files
            usersAll = [usersAll; thisUser];
    %         userAffilAll = [userAffilAll; thisAffil];
            userIDsAll = [userIDsAll; thisUserID];
            whichNeuron = [whichNeuron; thisNeuron];
        end
    end

    % get all unique user IDs
    uniUserIDs = unique(userIDsAll);

    % initialize trackers across users
    numNeurons = zeros(size(uniUserIDs));
    numEdits = zeros(size(uniUserIDs));
%     affil = cell(size(uniUserIDs));
    userNames = cell(size(uniUserIDs));
    
    % loop through all users
    for i = 1:length(uniUserIDs)
        % all entries for this user
        thisUserLog = userIDsAll == uniUserIDs(i);

        % all neurons for this user, unique only
        thisUserNeurons = whichNeuron(thisUserLog);
        uniNeurons = unique(thisUserNeurons);

        % add to trackers across users
        numNeurons(i) = length(uniNeurons);
        % each entry is an edit
        numEdits(i) = sum(thisUserLog);

        % get this user's name
        thisUserNames = usersAll(thisUserLog);
        userNames(i) = thisUserNames(1);

        % get this user's affiliation
%         thisUserAffil = userAffilAll(thisUserLog);
%         affil(i) = thisUserAffil(1);
    end

    % generate output table
%     outTable = table(uniUserIDs, userNames, affil, numEdits, numNeurons,...
%         'VariableNames',{'user_id', 'user name', 'affiliation', ...
%         'num edits', 'num neurons'});
    outTable = table(uniUserIDs, userNames, numEdits, numNeurons,...
        'VariableNames',{'user_id', 'user name',  ...
        'num edits', 'num neurons'});

    % write output table to CSV
    outCSVPath = [changeLogFolderPath filesep 'changeLogSummary.csv'];
    writetable(outTable, outCSVPath, 'Delimiter', ',');

end