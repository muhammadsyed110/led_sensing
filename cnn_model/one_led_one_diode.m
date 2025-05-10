global serialObj;

% --- 1) (Re-)initialize serial if needed ---
if isempty(who('global','serialObj')) || ~isvalid(serialObj)
    serialObj = serialport("COM3",115200);
    configureTerminator(serialObj,"LF");
    pause(2);    % wait for device
end

% --- 2) (Optional) turn everything off first ---
writeline(serialObj, "LAF");
pause(0.1);

% --- 3) Select (switch) the first LED at position (1,1) ---
writeline(serialObj, "LOX11");
pause(0.1);

% --- 4) Read back the raw line ---
raw = readline(serialObj);    
% raw will look like:  ',LOX11,3.030123'

% --- 5) Split & extract the third field as text ---
parts = split(raw, ',');
if numel(parts) < 3
    error("Unexpected response format: %s", raw);
end
rawValue = strtrim(parts{3});   % e.g. "3.030123"

% --- 6) Convert to double if you also want a numeric type ---
ledValue = str2double(rawValue);

% --- 7) Display ---
fprintf("Raw response           : %s\n", raw);
fprintf("Extracted raw value    : %s V\n", rawValue);
fprintf("Numeric value returned : %f V\n", ledValue);
