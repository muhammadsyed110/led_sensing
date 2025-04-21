
clear all
close all
clc
% Prompt user for file input
filename = "C:\___Downloads_Drive___\'''''''''THESIS____\00-LED_Grid\00-Collect_Data\LED_Matrix_2025_02_24_22_52_37.xlsx"; % Update if needed

displayType = select_display_type();

% Get sheet names
[~, sheets] = xlsfinfo(filename);

% Ensure sheets are in a cell array
if ischar(sheets)  
    sheets = {sheets}; % Convert single sheet to cell array
end

% Remove "Physical_Setup" sheet from the list
sheets = sheets(~strcmp(sheets, 'Physical_Setup'));
numSheets = length(sheets);


% Display available sheets
fprintf('Available Sheets:\n');
for i = 1:numSheets
    fprintf('%d: %s\n', i, sheets{i});
end


if (displayType == 1) || (displayType == 2)
   % Ask user for sheet selection
    sheetIndex = input('Enter the sheet number to display (or enter 0 for final output): ');
    
    % Validate input
    if sheetIndex < 0 || sheetIndex > numSheets
        disp('❌ Invalid sheet number! Exiting...');
        return;
    end

    % Read data from the selected sheet
    if sheetIndex == 0
        sheetName = 'Average'; % Final output sheet
    else
        sheetName = sheets{sheetIndex};
    end

    fprintf('📖 Reading data from sheet: %s\n', sheetName);
    dataTable = readtable(filename, 'Sheet', sheetName);

    % Convert table to numeric array (excluding first column)
    dataValues = table2array(dataTable(:, 2:end));
    
    
    % Display values in a readable grid format
    fprintf('📊 Grid Values (Scaled 0-1024):\n');
    [numRows, numCols] = size(dataValues);
    
    header_2nd_col = dataTable.Properties.VariableNames{2};

end


% % Automatically detect if LED values are in first row or first column
% if contains(header_2nd_col, 'LOX', 'IgnoreCase', true)
%     % First row contains LED values → Set as X-axis
%     xLabels = 'LED';
%     yLabels = 'Photo Diode';
% 
% else
%     % First column contains LED values → Set as Y-axis
%     yLabels = 'LED';
%     xLabels = 'Photo Diode';
% end

yLabels = 'LED';
xLabels = 'Photo Diode';


if (displayType == 1)
    visualize_grid(dataValues , filename,xLabels,yLabels);

elseif (displayType == 2)
    plot_5x5_grid(dataValues , filename,yLabels);

elseif displayType == 3

    % Get sheet names
   % [~, sheets] = xlsfinfo(filename);
   % numSheets = length(sheets);

    % Initialize combined data storage
    combinedColumn = [];

    
    for i = 1:numSheets
        sheetName = sheets{i};

        fprintf('📖 Reading data from sheet: %s\n', sheetName);

        dataTable = readtable(filename, 'Sheet', sheetName);
        firstColumn = table2array(dataTable(:, 2:end)); % Extract column 1 (excluding headers)
        
        % Append column values from this sheet to combined dataset
        combinedColumn = [combinedColumn; firstColumn]; 
    end
    %end

   
     plot_5x5_grid_all(combinedColumn , filename,yLabels);


else
    visualize_grid(dataValues , filename,xLabels,yLabels);

end


print_physical_setup_display(filename);


%%

% Dummy Function to Ask for Display Type
function choice = select_display_type()
    fprintf('\nSelect Display Type:\n');
    fprintf('1: Heatmap\n');
    fprintf('2: Graph\n');
    fprintf('3: Overall Graph\n');
    
    choice = input('Enter your choice (1-3): ');

    % Validate input
    if ~ismember(choice, [1, 2, 3])
        disp('❌ Invalid choice! Defaulting to Heatmap.');
        choice = 1;
    end

    
end



%%

function visualize_grid(dataValues, sheetName, X_Label, Y_Label)
    
    % Create the heatmap visualization
    figure;
    imagesc(dataValues, [0 1024]); % Set color scale from 0 to 1024
    colorbar;
    caxis([0 1024]); % Fix color range explicitly
    title(['Grid Visualization - ', sheetName]);
    xlabel(X_Label);
    ylabel(Y_Label);
    colormap(jet);
end

function plot_5x5_grid(dataValues, sheetName, Labels)
    % Get the number of columns
    [numRows, numCols] = size(dataValues);
    
    % Determine grid size (always 5 columns, extra rows if needed)
    gridRows = ceil(numCols / 5);
    gridCols = min(numCols, 5);

    % Create figure
    figure('Units', 'normalized', 'OuterPosition', [0 0 1 1]); % Full-screen figure
    sgtitle(['5x5 Grid Visualization - ', sheetName], 'FontSize', 16, 'FontWeight', 'bold'); % Main title

    % Loop through all columns and plot in grid format
    for col = 1:numCols
        subplot(gridRows, gridCols, col); % Create subplot in grid
        
        % Plot data for the current column
        plot(1:numRows, dataValues(:, col), 'o-', 'LineWidth', 1.5);
        hold on;

        % Formatting
        title(['Sensor ', num2str(col)]);
        xlabel(Labels);
        ylabel('Sensor Value');
        ylim([0 1024]); % Keep values within range
        grid on;
    end

    hold off;
end

function plot_5x5_grid_all(dataValues, sheetName, Labels)
    % Get the number of columns and rows
    [numRows, numCols] = size(dataValues);
    
    % Determine grid size (always 5 columns, extra rows if needed)
    gridRows = ceil(numCols / 5);
    gridCols = min(numCols, 5);

    % Define colors for different segments
    segmentColors = {'r', 'b', 'g', 'm', 'c', 'y', 'k'}; % Red, Blue, Green, Magenta, Cyan, Yellow, Black
    numSegments = length(segmentColors); % Number of color options
    segmentSize = 25; % Change color every 25 points

    % Create figure
    figure('Units', 'normalized', 'OuterPosition', [0 0 1 1]); % Full-screen figure
    sgtitle(['5x5 Grid Visualization - ', sheetName], 'FontSize', 16, 'FontWeight', 'bold'); % Main title

    % Loop through all columns and plot in grid format
    for col = 1:numCols
        subplot(gridRows, gridCols, col); % Create subplot in grid
        hold on;

        % Plot in segments of 25 with different colors
        for startIdx = 1:segmentSize:numRows
            endIdx = min(startIdx + segmentSize - 1, numRows); % Ensure within bounds
            colorIndex = mod(floor(startIdx / segmentSize), numSegments) + 1; % Cycle through colors
            plot(startIdx:endIdx, dataValues(startIdx:endIdx, col), 'o-', ...
                 'LineWidth', 1.5, 'Color', segmentColors{colorIndex});
        end
        
        % Formatting
        title(['Sensor ', num2str(col)]);
        xlabel(Labels);
        ylabel('Sensor Value');
        ylim([0 1024]); % Keep values within range
        grid on;
    end

    hold off;
end


function display_physical_setup(filename)
    % Read the "Physical_Setup" sheet
    [~, sheets] = xlsfinfo(filename);

    % Check if "Physical_Setup" sheet exists
    if ~ismember('Physical_Setup', sheets)
        errordlg('❌ "Physical_Setup" sheet not found!', 'Error');
        return;
    end

    % Read data from "Physical_Setup" sheet
    setup_data = readtable(filename, 'Sheet', 'Physical_Setup', 'ReadVariableNames', true);

    % Check if the expected column exists
    if ~ismember('Physical_Setup', setup_data.Properties.VariableNames)
        errordlg('❌ Column "Experiment_Setup" not found in the sheet!', 'Error');
        return;
    end

    % Extract text safely
    if iscell(setup_data.Physical_Setup)
        setup_text = setup_data.Physical_Setup{1}; % Use {} for cell array
    else
        setup_text = setup_data.Physical_Setup(1); % Use () for string array
    end

    % Create GUI figure with a larger window size
    fig = figure('Name', 'Physical Setup Information', 'NumberTitle', 'off', ...
                 'Position', [400, 200, 600, 400], ...  % Increased window size
                 'MenuBar', 'none', 'Resize', 'off');

    % Create title text
    uicontrol('Style', 'text', 'String', 'Physical Setup Information:', ...
              'FontSize', 14, 'FontWeight', 'bold', ...
              'Position', [150, 350, 300, 30]);

    % Display setup details in an editable multi-line text box
    uicontrol('Style', 'edit', 'String', setup_text, ...
              'FontSize', 12, 'Max', 2, 'Min', 0, 'Enable', 'inactive', ...
              'Position', [50, 100, 500, 250], ...  % Adjusted text box size
              'BackgroundColor', 'white');
end


function print_physical_setup_display(filename)
    % Read the "Physical_Setup" sheet
    [~, sheets] = xlsfinfo(filename);

    % Check if "Physical_Setup" sheet exists
    if ~ismember('Physical_Setup', sheets)
        fprintf('❌ Error: "Physical_Setup" sheet not found!\n');
        return;
    end

    % Read data from "Physical_Setup" sheet
    setup_data = readtable(filename, 'Sheet', 'Physical_Setup', 'ReadVariableNames', true);

    % % Check if the expected column exists
    % if ~ismember('Physical_Setup', setup_data.Properties.VariableNames)
    %     fprintf('❌ Error: Column "Physical_Setup" not found in the sheet!\n');
    %     return;
    % end

    % Extract text safely
    if iscell(setup_data.Physical_Setup)
        setup_text = setup_data.Physical_Setup{1}; % Use {} for cell array
    else
        setup_text = setup_data.Physical_Setup(1); % Use () for string array
    end

    % Print the setup information in the command window
    fprintf('\n🔍 **Physical Setup Information:**\n');
    fprintf('%s\n', setup_text);
end
