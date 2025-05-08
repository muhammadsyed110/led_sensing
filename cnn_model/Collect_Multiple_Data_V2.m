clc
clear all
global serialObj;

%%
% Device Setting
N = 5;  % Number of datasets
Port = "COM3";
BaudRate = 115200;


% Read and display experiment setup
setup_filename = 'Physical_Setup.txt';


% Generate a filename with the current date and time
timestamp = datestr(now, 'yyyy_mm_dd_HH_MM_SS'); % Format: YYYY-MM-DD_HH-MM-SS
filename = ['LED_Matrix_' timestamp '.xlsx']; % Final filename


 global LED_Diode_Selection;
 LED_Diode_Selection = input('Fixed LED  (0) or Fixed Diode  (1)', 's');



if isfile(setup_filename)
    % fileID = fopen(setup_filename, 'r');
    % setup_content = fscanf(fileID, '%c'); % Read entire file as text
    % 
    % fclose(fileID);
    
    fileID = fopen(setup_filename, 'r');
    rawData = textscan(fileID, '%s', 'Delimiter', '\n', 'Whitespace', '');
    fclose(fileID);
    rawData = rawData{1};
    
    % Write each line to a new row in Excel
    for i = 1:length(rawData)
        writecell({rawData{i}}, filename, 'Sheet', 'Physical_Setup', 'Range', ['A' num2str(i)]);
    end

    disp('🔍 Experiment Setup Configuration:');
    disp(rawData);
    
    % Ask for user confirmation
    confirm = input('Is the setup configuration correct? (y/n): ', 's');
    if lower(confirm) ~= "y"
        error('⚠️ Experiment setup configuration not confirmed. Stopping execution.');
    end
else
    error('⚠️ Experiment_Setup.txt not found. Please check the file location.');

end




%%
Initialize_Device(Port, BaudRate);

for sheet_num = 1:N
    data_table = collect_data(sheet_num);  % Call the function

    writetable(data_table, filename, 'Sheet', num2str(sheet_num)); % Save to Excel
end

clear serialObj

% Check if the serial object is successfully deleted
if ~exist('serialObj', 'var')
    disp('✅ Serial port closed successfully.');
else
    disp('⚠️ Failed to close the serial port.');
end

%% Implement Mathematical Operations here for smoothing data before processing it for machine learning

Average(filename);



%% Average

function Average(FileName)
    % Define file name
    filename = FileName;

    % Get sheet names
    [~, sheets] = xlsfinfo(filename);
    numSheets = length(sheets);
    
    % Filter sheets that have numeric names
    numericSheets = {};
    for i = 1:numSheets
        if all(isstrprop(sheets{i}, 'digit')) % Check if sheet name is numeric
            numericSheets{end+1} = sheets{i}; %#ok<AGROW>
        end
    end
    
    % Get the number of valid numeric sheets
    validSheetsCount = length(numericSheets);
    
    if validSheetsCount == 0
        disp('No numeric sheets found.');
        return;
    end
    
    % Read the first numeric sheet to get dimensions
    dataTable = readtable(filename, 'Sheet', numericSheets{1});
    [numRows, numCols] = size(dataTable);
    
    % Initialize sum matrix
    sumMatrix = zeros(numRows, numCols - 1); % Exclude first column (LOX)
    
    % Loop through numeric sheets and accumulate values
    for i = 1:validSheetsCount
        dataTable = readtable(filename, 'Sheet', numericSheets{i});
        dataValues = table2array(dataTable(:, 2:end)); % Exclude first column (LOX)
        
        % Replace NaN values with zeros for averaging
        dataValues(isnan(dataValues)) = 0;
        
        % Accumulate values
        sumMatrix = sumMatrix + dataValues;
    end
    
    % Compute the average
    avgMatrix = sumMatrix / validSheetsCount;
    
    % Prepare the output table
    averageTable = dataTable;
    averageTable{:, 2:end} = avgMatrix; 
    
    % Write the average data to a new sheet
    writetable(averageTable, filename, 'Sheet', 'Average');

    % Display result
    disp('Average values computed successfully:');
 
end

%% Utilities for AutoCollection of Data

function data_table = collect_data(sheet_num)

global LED_Diode_Selection;

    % Define the range for LOX and DON (5x5 grid)
    lox_range_x = 1:5;
    lox_range_y = 1:5;
    don_range_x = 1:5;
    don_range_y = 1:5;

    % Generate LOX labels (LOX11 to LOX55)
    lox_labels = {};
    for x = lox_range_x
        for y = lox_range_y
            lox_labels{end+1} = sprintf('LOX%d%d', x, y);
        end
    end

    % Generate DON labels (DON11 to DON55)
    don_labels = {};
    for x = don_range_x
        for y = don_range_y
            don_labels{end+1} = sprintf('DON%d%d', x, y);
        end
    end

    % Create a data matrix with LOX in the first column and DON values as headers
    num_lox = length(lox_labels);
    num_don = length(don_labels);
    data_matrix = cell(num_lox, num_don + 1);
    data_matrix(:,1) = lox_labels';  % First column = LOX values

    % Initialize all numerical values to NaN
    for i = 1:num_lox
        for j = 1:num_don
            data_matrix{i, j+1} = NaN; % Empty positions
        end
    end

    % Simulate received data (Replace this with actual data collection)
    received_data = {};


   received_data = {};
   if LED_Diode_Selection == '1'
        received_data = Arduino_Data_Collection_D();
   else
        received_data = Arduino_Data_Collection_L();
   end

    % for i = 1:randi([10, 25])  % Simulating different amounts of received data
    %     lox_idx = randi([1, num_lox]);
    %     don_idx = randi([1, num_don]);
    %     value = round(rand(), 2); % Generate random float values
    %     received_data{end+1} = sprintf('%s,%s,%.2f', lox_labels{lox_idx}, don_labels{don_idx}, value);
    % end

    % Process the received data and place it in the correct position
    for k = 1:length(received_data)
        thisLine = received_data{k};
        parts = split(thisLine, ',');

        if length(parts) < 3
            continue;
        end

        lox_str   = strtrim(parts{1});
        don_str   = strtrim(parts{2});
        val_str   = strtrim(parts{3});
        val = str2double(val_str);

        % Find LOX and DON positions
        lox_index = find(strcmp(lox_labels, lox_str), 1);
        don_index = find(strcmp(don_labels, don_str), 1);

        if ~isempty(lox_index) && ~isempty(don_index)
            data_matrix{lox_index, don_index + 1} = val;
        end
    end

    % Convert to table and add headers
    header = ['LOX', don_labels];
    data_table = cell2table(data_matrix, 'VariableNames', header);
end


function Received_Data = Arduino_Data_Collection_L

    global serialObj;
    
    %% Loop to Control LEDs and Diodes
    Received_Data = {}; % Initialize storage
    i = 1;
    
    for lx = 1:5
        for ly = 1:5
            lox_str = sprintf("LOX%d%d", lx, ly)
            Select_LED_L(lox_str);
            
            for dx = 1:5
                for dy = 1:5
                    don_str = sprintf("DON%d%d", dx, dy);
                    Received_Data{i,1} = Select_Diode_L(don_str);
                    i = i + 1;
                end
            end
        end
    end

end


function Received_Data = Arduino_Data_Collection_D

    global serialObj;
    
    %% Loop to Control LEDs and Diodes
    Received_Data = {}; % Initialize storage
    i = 1;

    for dx = 1:5
        for dy = 1:5
            don_str = sprintf("DON%d%d", dx, dy) % DON remains fixed
            Select_Diode_D(don_str);
            
            for lx = 1:5
                for ly = 1:5
                    lox_str = sprintf("LOX%d%d", lx, ly); % LOX changes
                    
                    Received_Data{i,1} = Select_LED_D(lox_str); % Read data
                    i = i + 1;
                end
            end
        end
    end

end



function Initialize_Device (Port, BaudRate)


    global serialObj;
    
    % Define the serial port object (replace 'COM3' with your port name)
    port = Port;  % Change this to your actual serial port
    baudRate = BaudRate; % Define baud rate, adjust as necessary
    
    % Create a serialport object
    serialObj = serialport(port, baudRate);
    
    % Configure the serial port object
    configureTerminator(serialObj, "LF"); % LF stands for Line Feed (\n)
    pause(5);
       
    %% All LED OFF
    % Write data to the serial port
    writeline(serialObj, "LAF");
    
    % Read data from the serial port until terminator
    receivedData = readline(serialObj)
    pause(1);
end


% Function Definitions
function Data = Select_Diode_L(Diode)
global serialObj;
writeline(serialObj, Diode);
Data = readline(serialObj);
%disp("Received Data:");
disp(Data);
end

function Data = Select_LED_L(LED)
global serialObj;
writeline(serialObj, LED);
receivedData = readline(serialObj);
end


% Function Definitions
function Data = Select_Diode_D(Diode)
global serialObj;
writeline(serialObj, Diode);
receivedData = readline(serialObj);
end

function Data = Select_LED_D(LED)
global serialObj;
writeline(serialObj, LED);
Data = readline(serialObj);
%disp("Received Data:");
disp(Data);

end

