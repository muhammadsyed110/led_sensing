import numpy as np
import pandas as pd
from collections import Counter

# Assuming you have a dataset with labels in `y_train`, `y_val`, etc.
# If your labels are in a pandas DataFrame or CSV file, load them like this:
# df = pd.read_csv("your_dataset.csv")
# y_train = df['label']

print("Unique classes in training set:", np.unique(y_train))
print("Class distribution:", Counter(y_train))
