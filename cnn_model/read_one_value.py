import serial
import json
import time

ser = serial.Serial("COM3", 115200, timeout=1)
time.sleep(2)

# Example: Read value when LED(1,1) and PD(1,1) are active
ser.write(b'LOX11\n')
time.sleep(0.1)
ser.write(b'DON11\n')
time.sleep(0.1)
ser.write(b'GETVAL\n')

line = ser.readline().decode().strip()
try:
    data = json.loads(line)
    print(f"LED: {data['LED']}, PD: {data['PD']}, Value: {data['val']}")
except json.JSONDecodeError:
    print("❌ Failed to parse:", line)

ser.close()
