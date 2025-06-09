import os
import torch
from torchviz import make_dot
from model import RowDetection  # assumes model.py is in the same folder

# Ensure Graphviz is available
os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin"

# Define the model
model = RowDetection(in_channel=3, out_channel=1).eval()

# Create dummy input (batch size 1, 3 channels, 384x384 image)
dummy_input = torch.randn(1, 3, 384, 384)

# Forward pass
output = model(dummy_input)

# Create diagram
dot = make_dot(output, params=dict(model.named_parameters()))
dot.format = "png"
dot.render("row_detection_model")  # This saves as row_detection_model.png

print("✅ Model diagram saved as 'row_detection_model.png'")
