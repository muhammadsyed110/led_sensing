# 🔬 LED Matrix Data Collection & Preprocessing Pipeline (MATLAB)

This stage of the pipeline handles real-world data collection from an LED matrix and photodiode hardware setup, using MATLAB. It creates, averages, and visualizes raw sensing data, and then prepares image and mask files for machine learning.

---

## ⚙️ Pipeline Overview

📡 Data Collection (.m) └── 🧾 Physical Setup (.txt) └── 📊 Data Visualization (.m) └── 🖼️ Image + Mask Creation & Dataset Split (.m)


---

## 📁 MATLAB Files Breakdown

### 1️⃣ [`Collect_Multiple_Data.m`](./matlabPipeline/Collect_Multiple_Data.m)

#### **Purpose:**
- Collects N (user-defined) measurements from the hardware via serial communication.
- Stores data in an Excel file with time-based naming.
- Averages across all measurements to reduce noise.
- Writes physical setup configuration details into the Excel file.

#### **Key Functions:**
- `Initialize_Device()` – Connects to the Arduino.
- `collect_data()` – Collects sensor data for a 5x5 LED/diode grid.
- `Average()` – Averages readings from multiple Excel sheets.
- `Arduino_Data_Collection_L()` / `D()` – Control which device remains fixed during data collection (LED or Diode).

![IMG20250224222229.jpg](images/IMG20250224222229.jpg)

![IMG20250224232735.jpg](images/IMG20250224232735.jpg)

![img_3.png](images/img_3.png)

---

### 2️⃣ [`Physical_Setup.txt`](./matlabPipeline/Physical_Setup.txt)

#### **Purpose:**
Defines physical parameters and grid layout of the experiment.

#### **Includes:**
- Object size (e.g., 3x3x5 cm)
- 13x15 grid layout with binary object occupancy matrix
- LED/diode method used (fixed LED or diode)
- Exact (x, y) positions of 5x5 LEDs
- Material type and shape
- Metadata like delay time, sample count, etc.

✅ This setup file is read and verified in `Collect_Multiple_Data.m`.

![img_2.png](images/img_2.png)

---

### 3️⃣ [`Data_Collection_Visualization.m`](./matlabPipeline/Data_Collection_Visualization.m)

#### **Purpose:**
Visualizes collected data from the Excel file.

#### **Features:**
- User chooses heatmap or graph visualization.
- Can visualize individual or all sheets.
- Shows sensor values in 5x5 grid layout.
- Displays values scaled to 0–1024.
- Also prints physical setup info to console or GUI.

### **HeatMap**
![Heatmap_LED_Matrix_2025_02_24_23_24_01.jpg](images/Heatmap_LED_Matrix_2025_02_24_23_24_01.jpg)

### **Graph**
![Graph_LED_Matrix_2025_02_24_23_24_01.jpg](images/Graph_LED_Matrix_2025_02_24_23_24_01.jpg)

### **Overall Graph**
![Overall_Graph_LED_Matrix_2025_02_24_23_24_01.jpg](images/Overall_Graph_LED_Matrix_2025_02_24_23_24_01.jpg)
---

### 4️⃣ [`Data_Image_Mask.m`](./matlabPipeline/Data_Image_Mask.m)

#### **Purpose:**
Processes the Excel files to create image/mask datasets.

#### **Steps:**
1. **Reads binary matrix from `Physical_Setup` sheet**  
   → Generates **mask images** (binary object segmentation).

![img_4.png](images/img_4.png)

2. **Reads averaged sensor data**  
   → Converts to **grayscale images** for model input.

![img_6.png](images/img_6.png)

3. **Preprocessing:**  
   - Resizes and normalizes images.
   - Converts each `.xlsx` file into multiple `.png` images.

4. **Dataset Split:**  
   - Shuffles and splits all images/masks into:
     - `train/`
     - `val/`
     - `test/`

✅ Output ready for training with U-Net model or other segmentation frameworks.

---

## 🗂️ Output Structure

📁 99-ImagePreProcessing/ ├── Images/ └── Masks/ 📁 99-Splited_Data(for training)/ ├── train/ ├── val/ └── test/


---

## 🔧 Requirements

To run these files, make sure you have:
- MATLAB (R2020+ recommended)
- A working serial connection to the LED/photodiode hardware
- Excel installed (for reading/writing `.xlsx`)
- Properly updated file paths in the `.m` scripts

---


# 🤖 LED Matrix Object Detection – Machine Learning Pipeline

This part of the project focuses on detecting object positions from preprocessed LED matrix data using a deep learning approach. It uses a U-Net segmentation model trained on grayscale sensor images and corresponding binary masks.

---

## 🔁 Pipeline Flow

```mermaid
graph TD;
    A[Grayscale Images & Binary Masks] --> B[Data Preprocessing]
    B --> C[U-Net Model Training]
    C --> D[Prediction & Visualization]
```

### 🧠 Overview of Jupyter Notebooks
### 📓 1. 01-Data_Preprocessing.ipynb
→ Prepares input data for model training

### 🔍 What it does:
Loads image and mask .png files

Resizes them to uniform dimensions (e.g., 128x128)

Normalizes image pixel values to range [0, 1]

Converts mask to binary format

Splits data into train, val, and test sets

🧪 Example Code Snippets:
```
# Load images and masks
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

# Resize to 128x128
image = cv2.resize(image, (128, 128))
mask = cv2.resize(mask, (128, 128))

# Normalize input
image = image / 255.0

# Convert mask to binary
mask = (mask > 127).astype(np.uint8)
```
```
# Train-validation-test split
from sklearn.model_selection import train_test_split

X_train, X_temp, y_train, y_temp = train_test_split(images, masks, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
```
✅ Output: NumPy arrays → X_train, y_train, etc.

### 📓 2. 02-LED_Matrix_Train_Model.ipynb
→ Trains a U-Net model on the preprocessed dataset

### 🧠 What it does:
Defines a U-Net architecture using TensorFlow/Keras

Compiles the model with binary cross-entropy loss

Trains using the train and validation sets

Monitors performance with training curves

Saves the best performing model

### 🧪 Example Code Snippets:
```
def unet_model(input_size=(128,128,1)):
    inputs = Input(input_size)
    # ... Add convolution, pooling, upsampling layers ...
    outputs = Conv2D(1, (1, 1), activation='sigmoid')(conv7)
    return Model(inputs=[inputs], outputs=[outputs])
```
```
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=20,
    batch_size=8
)
```
✅ Output: Trained model saved as unet_model.h5

### 📓 3. 03-LED_Matrix_Prediction.ipynb
→ Predicts object positions and visualizes results

### 🔍 What it does:
Loads the trained model

Predicts masks for new or test images

Displays input image, ground truth, and prediction side-by-side

Computes evaluation metrics (IoU, Dice, etc.)

### 🧪 Example Code Snippets:
```meramid
model = tf.keras.models.load_model('unet_model.h5')

pred = model.predict(np.expand_dims(X_test[0], axis=0))
pred_mask = (pred[0] > 0.5).astype(np.uint8)
```
```
# Visualize results
plt.figure(figsize=(10, 4))
plt.subplot(1, 3, 1)
plt.title("Input Image")
plt.imshow(X_test[0].squeeze(), cmap='gray')

plt.subplot(1, 3, 2)
plt.title("Ground Truth")
plt.imshow(y_test[0].squeeze(), cmap='gray')

plt.subplot(1, 3, 3)
plt.title("Prediction")
plt.imshow(pred_mask.squeeze(), cmap='gray')
plt.show()
```
✅ Output: Side-by-side plots and metrics for segmentation quality

### ⚙️ Installation
### 🐍 Required Python Libraries
Create a virtual environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
```
pip install numpy matplotlib opencv-python scikit-learn tensorflow
```
Or use:
```
pip install -r requirements.txt
```
### 🚀 Running the Pipeline
1. 📁 Place your images and masks in organized folders (e.g., Images/ and Masks/)

2. ▶️ Run 01-Data_Preprocessing.ipynb to prepare your training data

3. 🧠 Run 02-LED_Matrix_Train_Model.ipynb to train the model

4. 🔍 Run 03-LED_Matrix_Prediction.ipynb to test the model and visualize predictions

