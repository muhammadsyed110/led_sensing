import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('../dataset.csv')

X_cols = [f'X{i}' for i in range(25)]
Y_cols = [f'Y{i}' for i in range(25)]

# Group by unique object positions
unique_positions = df[X_cols].drop_duplicates()

for idx, pos in unique_positions.iterrows():
    mask = (df[X_cols] == pos.values).all(axis=1)
    avg_Y = df.loc[mask, Y_cols].mean().values.reshape(5,5)

    plt.imshow(avg_Y, cmap='viridis')
    plt.title(f'Avg Sensor Output for Position {idx+1}')
    plt.colorbar()
    plt.show()
