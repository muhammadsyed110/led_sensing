function get_machinedata()
clc;
clear all;
global serialObj;
global LED_Diode_Selection;

%% Settings
LED_Diode_Selection = '1'; % '0' = Fixed LED, '1' = Fixed Diode
Port = "COM3";             % Replace with your actual port if needed
BaudRate = 115200;

% Initialize serial connection
Initialize_Device(Port, BaudRate);

% Collect data once (5x5 matrix)
data_table = collect_data(1);

% Convert to numeric matrix (remove LOX label column)
data_array = table2array(data_table(:, 2:end));

% Save matrix to a text file (space-delimited)
writematrix(data_array, 'machineoutput.txt', 'Delimiter', ' ');

% Cleanup
clear serialObj;
disp('✅ machineoutput.txt saved successfully.');
end

%% ======== Helper Functions Below ===========

function Initialize_Device(Port, BaudRate)
    global serialObj;
    serialObj = serialport(Port, BaudRate);
    configureTerminator(serialObj, "LF");
    pause(5);  % wait for Arduino to be ready
    writeline(serialObj, "LAF"); % Turn all LEDs off
    readline(serialObj);         % Read confirmation
    pause(1);
end

function data_table = collect_data(~)
    global LED_Diode_Selection;

    % Define 5x5 label ranges
    lox_labels = {};
    don_labels = {};
    for x = 1:5
        for y = 1:5
            lox_labels{end+1} = sprintf('LOX%d%d', x, y);
            don_labels{end+1} = sprintf('DON%d%d', x, y);
        end
    end

    num_lox = length(lox_labels);
    num_don = length(don_labels);
    data_matrix = cell(num_lox, num_don + 1);
    data_matrix(:,1) = lox_labels';

    for i = 1:num_lox
        for j = 1:num_don
            data_matrix{i, j+1} = NaN;
        end
    end

    % Collect actual data via Arduino
    if LED_Diode_Selection == '1'
        received_data = Arduino_Data_Collection_D();
    else
        received_data = Arduino_Data_Collection_L();
    end

    % Parse received data into matrix
    for k = 1:length(received_data)
        parts = split(received_data{k}, ',');
        if length(parts) < 3, continue; end
        lox = strtrim(parts{1});
        don = strtrim(parts{2});
        val = str2double(strtrim(parts{3}));
        li = find(strcmp(lox_labels, lox));
        di = find(strcmp(don_labels, don));
        if ~isempty(li) && ~isempty(di)
            data_matrix{li, di+1} = val;
        end
    end

    header = ['LOX', don_labels];
    data_table = cell2table(data_matrix, 'VariableNames', header);
end

function Received_Data = Arduino_Data_Collection_L()
    global serialObj;
    Received_Data = {};
    i = 1;
    for lx = 1:5
        for ly = 1:5
            lox_str = sprintf("LOX%d%d", lx, ly);
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

function Received_Data = Arduino_Data_Collection_D()
    global serialObj;
    Received_Data = {};
    i = 1;
    for dx = 1:5
        for dy = 1:5
            don_str = sprintf("DON%d%d", dx, dy);
            Select_Diode_D(don_str);
            for lx = 1:5
                for ly = 1:5
                    lox_str = sprintf("LOX%d%d", lx, ly);
                    Received_Data{i,1} = Select_LED_D(lox_str);
                    i = i + 1;
                end
            end
        end
    end
end

function Data = Select_Diode_L(Diode)
    global serialObj;
    writeline(serialObj, Diode);
    Data = readline(serialObj);
end

function Data = Select_LED_L(LED)
    global serialObj;
    writeline(serialObj, LED);
    readline(serialObj);
end

function Data = Select_Diode_D(Diode)
    global serialObj;
    writeline(serialObj, Diode);
    readline(serialObj);
end

function Data = Select_LED_D(LED)
    global serialObj;
    writeline(serialObj, LED);
    Data = readline(serialObj);
end
