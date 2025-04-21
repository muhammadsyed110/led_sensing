clear all
close all
clc

%% Must Correct These paths
% Define input folder path (change this as needed)
inputFolder ="C:\110_DATA\THESIS\00-LED_Grid\00-Collect_Data"; % Change this
Train_Data_baseDir = "C:\110_DATA\THESIS\00-LED_Grid\99-Splited_Data(for training)\train_data";  % change accordingly

Images_baseDir = "C:\110_DATA\THESIS\00-LED_Grid\99-ImagePreProcessing\Images";  % change accordingly
Masks_baseDir = "C:\110_DATA\THESIS\00-LED_Grid\99-ImagePreProcessing\Masks";  % change accordingly

%%

% Get the parent folder of inputFolder
[parentFolder, ~, ~] = fileparts(inputFolder);

% Dynamically define output folders inside the parent folder
outputFolderMask = fullfile(parentFolder, '99-ImagePreProcessing', 'Masks');
outputFolderImages = fullfile(parentFolder, '99-ImagePreProcessing', 'Images');



% Ensure the output folder exists
if ~exist(outputFolderMask, 'dir')
    mkdir(outputFolderMask);
end

% Ensure the output folder exists
if ~exist(outputFolderMask, 'dir')
    mkdir(outputFolderMask);
end

% Get a list of all .xlsx files in the input folder
fileList = dir(fullfile(inputFolder, '*.xlsx'));
fileList = fileList(~startsWith({fileList.name}, '~$'));



% Process each Excel file in the folder
for i = 1:length(fileList)
    
    % Get the full file path
    inputFile = fullfile(inputFolder, fileList(i).name);
    
    [~, name, ~] = fileparts(inputFile);
    
    fprintf('📖 Reading data from File: %s\n', name);
    %fprintf('📖 Reading data from sheet: %s\n', sheetName);

    % Call function to process and save image
    binary_matrix_to_image(inputFile, outputFolderMask);

    Grid_Images(inputFile, outputFolderImages);


end

disp('✅ Processing complete! All images saved in the output folder.');


disp('📖 Shuffling and spliting data into train, test and validataion');

split_dataset(Train_Data_baseDir,Images_baseDir, Masks_baseDir);


%% Making Train, test and validation dataset

function split_dataset(baseDir, images_data, mask_data)
    % Base paths
    
    imageDir = fullfile(baseDir, 'Image');
    maskDir = fullfile(baseDir, 'mask');

    test_dir = fullfile(imageDir, 'test');
    train_dir = fullfile(imageDir, 'train');
    val_dir = fullfile(imageDir, 'val');

    % Get all image files
    imageFiles = dir(fullfile(images_data, '*.png')); % change extension if needed
    totalImages = numel(imageFiles);

    
     % Get all image files
    imageFiles_m = dir(fullfile(mask_data, '*.png')); % change extension if needed
    totalImages_m = numel(imageFiles_m);
    

    idx = randperm(totalImages_m);
    numMask = round(1.0 * totalImages_m);
    maskIdx = idx(1:numMask);

    
    % Shuffle
    rng(0);
    idx = randperm(totalImages);

    % Split sizes
    numTrain = round(0.8 * totalImages);
    numVal = round(0.1 * totalImages);
    numTest = totalImages - numTrain - numVal;

    % Indices
    trainIdx = idx(1:numTrain);
    valIdx   = idx(numTrain+1:numTrain+numVal);
    testIdx  = idx(numTrain+numVal+1:end);

    % Create folders
    mkdir_if_missing(fullfile(train_dir));
    mkdir_if_missing(fullfile(val_dir));
    mkdir_if_missing(fullfile(test_dir));
    mkdir_if_missing(fullfile(maskDir));

    % Move files
    move_files(imageFiles, trainIdx, train_dir);
    move_files(imageFiles, valIdx,  val_dir);
    move_files(imageFiles, testIdx, test_dir);

    move_files(imageFiles_m, maskIdx, maskDir);


    disp('✅ Done splitting images and masks!');
end

function mkdir_if_missing(folder)
    if ~exist(folder, 'dir')
        mkdir(folder);
    end
end

function move_files(imageFiles, indices, copyLocation)
    % Create destination folder if it doesn't exist
    if ~exist(copyLocation, 'dir')
        mkdir(copyLocation);
    end

    % Copy each selected file
    for i = indices
        imgName = imageFiles(i).name;
        srcPath = fullfile(imageFiles(i).folder, imgName);
        dstPath = fullfile(copyLocation, imgName);

        copyfile(srcPath, dstPath);
    end
end





%% Function to Convert Binary Matrix from Excel to JPG Image for (Mask Only)
function binary_matrix_to_image(filename, outputFolderMask)

% Define the sheet name to read
sheetName = 'Physical_Setup';
  
% Extract only the file name (without extension)
    [~, name, ~] = fileparts(filename);
    
    % Generate the output image file name (save in output folder)
    % outputFile = fullfile(outputFolderMask, ['\',name, '_Mask.jpg'])
    % outputFile = strcat(outputFolderMask, '\', name, '_Mask.jpg');
       

% Read data from the Excel sheet
    binaryMatrix = read_binary_matrix_from_excel(filename, sheetName);
    
    % If data is empty, exit
    if isempty(binaryMatrix)
        disp(['❌ Error: No valid data found in ', filename]);
        return;
    end

    % Convert binary values (0/1) to grayscale (0 = black, 255 = white)
    imageData = uint8(binaryMatrix * 255); % Scale 0/1 to 0-255
    imageData = resize_binary_image_mask(imageData);
    
     % Get sheet names
    [~, sheets] = xlsfinfo(filename);

    % Ensure sheets are in a cell array
    if ischar(sheets)  
        sheets = {sheets}; % Convert single sheet to cell array
    end

    % Remove "Physical_Setup" sheet from the list
    sheets = sheets(~strcmp(sheets, 'Physical_Setup'));
    numSheets = length(sheets);
   

    % Ensure output folder exists
    if ~exist(outputFolderMask, 'dir')
        mkdir(outputFolderMask);
    end

    % Extract file name without extension
    [~, name, ~] = fileparts(filename);

    % Process each sheet
    for i = 1:numSheets
        sheetName = sheets{i};
        %fprintf('📖 Reading data from sheet: %s\n', sheetName);

        try
           % Define output file path
            % outputFile = fullfile(outputFolderImages, [name, '_', sheetName,'.jpg']);
            outputFile = strcat(outputFolderMask,'\', name, '_', sheetName,'.png');
            
            % Save the image
            imwrite(imageData, outputFile);
            disp(['✅ Image saved: ', outputFile]);

            
        catch ME
            fprintf('❌ Error processing %s: %s\n', sheetName, ME.message);
        end
    end
  
end

function resizedImage = resize_binary_image_mask(imageData)
    % Convert to logical
    logicalImage = imageData == 255;

    % Repeat each pixel: 26 times vertically (rows), 30 times horizontally (cols)
    enlargedImage = kron(logicalImage, true(26, 30));

    % Crop 3 pixels from all sides
    croppedImage = enlargedImage(4:end-3, 4:end-3);

    % Convert back to 0 or 255 format
    resizedImage = uint8(croppedImage) * 255;
end



%% Function to Read Binary Matrix from Excel
function binaryMatrix = read_binary_matrix_from_excel(filename, sheetName)
    try
        rawTable = readtable(filename, 'Sheet', sheetName, 'PreserveVariableNames', true);
    catch
        disp(['❌ Error: Unable to read "', sheetName, '" sheet in file: ', filename]);
        binaryMatrix = [];
        return;
    end

    % Convert table to cell array (preserves text format)
    rawData = table2cell(rawTable);

    % Extract rows 12 to 26 (adjust for MATLAB 1-based indexing)
    startRow = 11;
    endRow = 25;

    % Ensure data has enough rows
    if size(rawData, 1) < endRow
        disp(['❌ Error: Not enough rows in "', sheetName, '" in file: ', filename]);
        binaryMatrix = [];
        return;
    end

    % Extract only the relevant rows
    extractedData = rawData(startRow:endRow, :);

    % Convert space-separated strings into numeric arrays
    numRows = length(extractedData);
    numCols = 13; % Each row should have 13 values
    binaryMatrix = zeros(numRows, numCols); % Pre-allocate matrix

    for i = 1:numRows
        % Convert each row from string to numeric array
        binaryMatrix(i, :) = str2num(extractedData{i});
    end
end

%% PreProcessing: Data Image

function Grid_Images(filename, outputFolderImages)
    % Get sheet names
    [~, sheets] = xlsfinfo(filename);

    % Ensure sheets are in a cell array
    if ischar(sheets)  
        sheets = {sheets}; % Convert single sheet to cell array
    end

    % Remove "Physical_Setup" sheet from the list
    sheets = sheets(~strcmp(sheets, 'Physical_Setup'));
    numSheets = length(sheets);

    % % Display available sheets
    % fprintf('Available Sheets:\n');
    % for i = 1:numSheets
    %     fprintf('%d: %s\n', i, sheets{i});
    % end

    % Ensure output folder exists
    if ~exist(outputFolderImages, 'dir')
        mkdir(outputFolderImages);
    end

    % Extract file name without extension
    [~, name, ~] = fileparts(filename);

    % Process each sheet
    for i = 1:numSheets
        sheetName = sheets{i};
        %fprintf('📖 Reading data from sheet: %s\n', sheetName);

        try
            % Read the table
            dataTable = readtable(filename, 'Sheet', sheetName, 'PreserveVariableNames', true);

            % Convert to numeric matrix (skip first column which has text)
            rawData = table2array(dataTable(:, 2:end));  % Skip first column

            % Extract required rows and columns
            startRow = 1; endRow = 25;
            startCol = 1; endCol = 25;

            % Check if data is large enough
            if size(rawData, 1) < endRow || size(rawData, 2) < endCol
                fprintf('❌ Skipping %s: Not enough data.\n', sheetName);
                continue;
            end

            % Extract relevant numeric data
            numericMatrix = rawData(startRow:endRow, startCol:endCol);
            
            % Replace NaN values with 0
            numericMatrix(isnan(numericMatrix)) = 0;

            % % Normalize data to 0-1024 range
            % minValue = min(numericMatrix(:));
            % maxValue = max(numericMatrix(:));
            % 
            % if maxValue == minValue
            %     imageData = zeros(size(numericMatrix), 'uint8'); % Black image if all values are same
            % else
            %     imageData = uint8(255 * (numericMatrix - minValue) / (maxValue - minValue)); % Convert to uint8
            % end

            imageData = uint8(255 * (numericMatrix / 1024.0)); % Convert to uint8

            imageData = resize_binary_image_data_image(imageData);

            % Define output file path
            % outputFile = fullfile(outputFolderImages, [name, '_', sheetName,'.jpg']);
            outputFile = strcat(outputFolderImages,'\', name, '_', sheetName,'.png');
            % (outputFolderMask, '\', name, '_Mask.jpg')

            % Save the image
            imwrite(imageData, outputFile);
            fprintf('✅ Image saved: %s\n', outputFile);

        catch ME
            fprintf('❌ Error processing %s: %s\n', sheetName, ME.message);
        end
    end
end



function resizedImage = resize_binary_image_data_image(imageData)
    % Ensure input is uint8 (in case it's not)
    imageData = uint8(imageData);

    % Repeat each pixel into a 16x16 block (preserve grayscale values)
    enlargedImage = repelem(imageData, 16, 16);

    % Crop 8 pixels from all sides
    croppedImage = enlargedImage(9:end-8, 9:end-8);

    % Output the resized image
    resizedImage = croppedImage;
end









