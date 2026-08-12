import bme680
import time
import datetime
import grovepi
import csv

# Initialize BME680 sensor
try:
    bme_sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    bme_sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# Configure oversampling
bme_sensor.set_temperature_oversample(bme680.OS_8X)
bme_sensor.set_pressure_oversample(bme680.OS_4X)
bme_sensor.set_humidity_oversample(bme680.OS_2X)
bme_sensor.set_filter(bme680.FILTER_SIZE_3)

# Define GrovePi sensor ports
mq3_sensor = 1           # MQ3 sensor on analog port A1
hcho_sensor = 2          # HCHO sensor on analog port A2

# CSV file to store data
filename = "device.csv"

# Column headers
headers = [
    "Timestamp", "Normalized Timestamp (s)", "Temperature (C)", "Pressure (hPa)", "Humidity (%)",
    "VOC (ppm)", "CO2 (ppm)", "MQ3 (ppm)", "HCHO (ppm)"
]

# Write headers to CSV
with open(filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

# Conversion functions based on sensor datasheets
def convert_voc(raw_value):
    return round(raw_value * 0.1, 2)  # Example scale

def convert_co2(raw_value):
    return round(raw_value * 0.05, 2)  # Example scale

def convert_mq3(raw_value):
    return round(raw_value * 0.1, 2)  # Example scale

def convert_hcho(raw_value):
    return round(raw_value * 0.05, 2)  # Example scale

# Record the start time for normalized timestamps
start_time = time.time()

# Main data collection loop
try:
    while True:
        # Current time and normalized timestamp
        current_time = datetime.datetime.now()
        normalized_time = round(time.time() - start_time, 2)

        # Read BME680 data
        if bme_sensor.get_sensor_data():
            temperature = round(bme_sensor.data.temperature, 2)
            pressure = round(bme_sensor.data.pressure, 2)
            humidity = round(bme_sensor.data.humidity, 2)
        else:
            temperature = pressure = humidity = 0.0  # fallback if read fails

        # GrovePi sensor data
        voc = grovepi.analogRead(mq3_sensor)
        co2 = grovepi.analogRead(hcho_sensor)
        mq3_value = grovepi.analogRead(mq3_sensor)
        hcho_value = grovepi.analogRead(hcho_sensor)

        # Convert raw sensor values to meaningful units
        voc_ppm = convert_voc(voc)
        co2_ppm = convert_co2(co2)
        mq3_ppm = convert_mq3(mq3_value)
        hcho_ppm = convert_hcho(hcho_value)

        # Prepare data row
        data_row = [
            current_time, normalized_time, temperature, pressure, humidity,
            voc_ppm, co2_ppm, mq3_ppm, hcho_ppm
        ]

        # Write data row to CSV
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data_row)

        # Print data row for reference
        print(data_row)

        # Wait 0.1 seconds before next reading
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Data collection stopped.")

