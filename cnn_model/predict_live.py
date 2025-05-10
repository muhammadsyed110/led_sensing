# Create the final combined script that uses sensor_reader to collect matrix and predicts using CNN

predict_script = """
from sensor_reader import collect_sensor_matrix
from cnn_led_classifier_with_predict import predict_new_sample

def run_live_prediction():
    print("📡 Collecting real-time sensor matrix...")
    matrix = collect_sensor_matrix()
    print("📊 Predicting object position...")
    predict_new_sample(matrix)

if __name__ == '__main__':
    run_live_prediction()
"""

# Save the script as predict_live.py
predict_file_path = "/mnt/data/predict_live.py"
with open(predict_file_path, "w") as f:
    f.write(predict_script)

predict_file_path
