"""
        3D Printed Strain Gauge Gesture Recognition Project
          This script monitors a specified com port for incoming strain gauge data.
          The measurements are captured and stored in a datetime stamped .csv file.
          Author: Kevin Kasper (kasper@email.arizona.edu)
          Last edit:  06/01/2021
"""

import os
import serial
import datetime
import time
import pandas as pd

# Constant declarations. 'nt' refers to windows, which uses backslashes for directory paths.
# Otherwise we use forward slash for directory paths.
if os.name == 'nt':
    DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "data\\")
else:
    DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), "data/")
DATA_FOLDER_PATH = os.path.join(os.path.dirname(__file__), "data")

# Specify your com port and speed here.
# Check the Arduino IDE port selector to see which port to use. Speed is defined in the arduino script init.
COM_PORT = "COM8"
COM_SPEED = 115200

output_file_name = ""
outputData = {}


# Dynamically creates a .csv file in a 'data/' directory and timestamps the file.
def create_csv_if_not_exist():
    global output_file_name
    now = datetime.datetime.now()
    date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
    output_file_name = DATA_FILE_PATH + "strainCapture-" + date_time + ".csv"
    if not os.path.exists(output_file_name):
        os.makedirs(DATA_FOLDER_PATH, exist_ok=True)
    else:
        num = 1
        while os.path.exists(output_file_name):
            output_file_name = DATA_FILE_PATH + "capture " + date_time + "(" + str(num) + ")" + ".csv"
            num += 1

    # Create pandas dataframe and headers for each data column
    new_file_headers = pd.DataFrame(columns=['Time:', "Gauge 1:", "Gauge 2:", "Gauge 3:"])
    new_file_headers.to_csv(output_file_name, encoding='utf-8', index=False)
    print("Created log file: " + output_file_name)


if __name__ == "__main__":
    try:
        # Open a serial port connection. Return all bytes received between timeout (in seconds).
        ser = serial.Serial(COM_PORT, COM_SPEED, timeout=0.1)
    except serial.serialutil.SerialException as e:
        print("Could not open " + COM_PORT + ". Please check your settings. Is the device connected?")
        quit()

    create_csv_if_not_exist()

    # Clear the serial line in case we try to read in the middle of a write
    ser.flushInput()

    while True:
        try:
            result = ser.readline()
            if result:
                resultStr = result.decode('ascii').strip()          # Strip to remove /r and newline characters
                parsedData = resultStr.split(',')
                outputData = {
                    'Time:': [time.time()],                         # Use time as index
                    "Gauge 1:": parsedData[0],
                    "Gauge 2:": parsedData[1],
                    "Gauge 3:": parsedData[2]
                    }
                print(outputData)

                new_df = pd.DataFrame(outputData)
                new_df.to_csv(output_file_name, index=False, header=False, mode='a')   # Append data to csv file

        except KeyboardInterrupt:
            print("Keyboard Interrupt.")
            break
        except IndexError:
            pass
        except TypeError:
            print("Invalid data received.")
            pass
        except serial.serialutil.SerialException:
            print("Lost connection to serial device. Please double check your connection.")
            quit()
