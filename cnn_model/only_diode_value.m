function get_machinedata()
    %GET_MACHINEDATA Reads 5×5 diode values from serial, saves to machineoutput.txt,
    % and displays a heatmap of the results.
    
    clc; clear all;
    global serialObj;
    
    %% Settings
    Port     = "COM3";    % <-- Change if needed
    BaudRate = 115200;
    
    % 1) Initialize serial connection
    Initialize_Device(Port, BaudRate);
    
    % 2) Read the 5×5 diode grid
    data_array = collect_diode_data();
    
    % 3) Save to text file (5 rows × 5 values, space-delimited)
    writematrix(data_array, 'machineoutput.txt', 'Delimiter', ' ');
    disp('✅ machineoutput.txt saved successfully.');
    
    % 4) Plot the heatmap
    figure('Name','Machine Data Heatmap','NumberTitle','off');
    imagesc(data_array);
    colormap('parula');                % MATLAB built-in
    cb = colorbar;                     % get handle
    ylabel(cb, 'Value');               % set label
    axis equal tight;
    xlabel('Diode Column (y)');
    ylabel('Diode Row (x)');
    title('Machine Output Diode Heatmap');
    
    % 5) Cleanup
    clear serialObj;
end

%% === Helper functions ===

function Initialize_Device(Port, BaudRate)
    % Opens the serial port and flushes startup chatter.
    global serialObj;
    serialObj = serialport(Port, BaudRate);
    configureTerminator(serialObj, "LF");
    pause(2);                     % allow Arduino reset
    writeline(serialObj, "LAF");  % (optional) turn LEDs off
    pause(0.5);
    % Flush any initial response
    while serialObj.NumBytesAvailable > 0
        readline(serialObj);
    end
end

function data = collect_diode_data()
    % Sends DONxy commands for x,y=1..5 and parses the numeric part.
    global serialObj;
    
    data = zeros(5,5);  % pre-allocate
    
    for dx = 1:5
        for dy = 1:5
            cmd = sprintf("DON%d%d", dx, dy);
            writeline(serialObj, cmd);
            
            raw = readline(serialObj);
            parts = split(raw, ',');
            
            if numel(parts) >= 3
                val = str2double(strtrim(parts{3}));
                if isnan(val)
                    warning("Parsed NaN for %s from '%s'", cmd, raw);
                end
            else
                warning("Unexpected format for %s: '%s'", cmd, raw);
                val = NaN;
            end
            
            data(dx,dy) = val;
        end
    end
end
