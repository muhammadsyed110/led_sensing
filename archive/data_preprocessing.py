import pandas as pd
import numpy as np

X_list = []
Y_list = []

# Adjust range depending on how many sheets (1-indexed)
for i in range(0, 50):
    input_sheet = f"input{i+1}"
    output_sheet = f"output{i+1}"

    input_df = pd.read_excel("your_file.xlsx", sheet_name=input_sheet, header=None)
    output_df = pd.read_excel("your_file.xlsx", sheet_name=output_sheet, header=None)

    X_list.append(input_df.values)
    Y_list.append(output_df.values)

X = np.array(X_list)
Y = np.array(Y_list)
