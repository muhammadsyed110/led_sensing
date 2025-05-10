function get_machinedata()
    %GET_MACHINEDATA Reads 5×5 diode values from serial, saves to machineoutput.txt,
    % and displays a heatmap with the numeric values overlaid.
    
    clc; clear all;
    global serialObj;
    
    %% Settings
    Port     = "COM3";    % <-- Change as needed
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
    colormap('parula');                % MATLAB built-in colormap
    cb = colorbar;                     % get handle
    ylabel(cb, 'Value');               % label colorbar
    axis equal tight;
    xlabel('Diode Column (y)');
    ylabel('Diode Row    (x)');
    title('Machine Output Diode Heatmap');
    
    % 5) Overlay numeric values in each cell
    [nRows, nCols] = size(data_array);
    clim = get(gca, 'CLim');           % color limits for contrast decision
    mid = mean(clim);
    for i = 1:nRows
        for j = 1:nCols
            val = data_array(i,j);
            txt = sprintf('%.2f', val);
            % choose text color for readability
            if val > mid
                txtColor = [0 0 0];   % dark text on bright background
            else
                txtColor = [1 1 1];   % white text on dark background
            end
            text(j, i, txt, ...
                'HorizontalAlignment', 'center', ...
                'VerticalAlignment',   'middle', ...
                'Color', txtColor, ...
                'FontSize', 10);
        end
    end
    
    % 6) Cleanup
    clear serialObj;
end

%% === Helper functions ===

function Initialize_Device(Port, BaudRate)
    % Opens the serial port and flushes any startup chatter.
    global serialObj;
    serialObj = serialport(Port, BaudRate);
    configureTerminator(serialObj, "LF");
    pause(2);                     % allow device to reset
    writeline(serialObj, "LAF");  % (optional) turn LEDs off
    pause(0.5);
    % Flush initial responses
    while serialObj.NumBytesAvailable > 0
        readline(serialObj);
    end
end

function data = collect_diode_data()
    % Sends DONxy commands for x,y = 1..5 and parses the returned value.
    global serialObj;
    
    data = zeros(5,5);  % pre-allocate matrix
    
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
