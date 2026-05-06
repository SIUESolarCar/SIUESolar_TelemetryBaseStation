import can
import cantools
from dotenv import load_dotenv
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from InfluxCANTools import InfluxCANTools

# token = os.getenv('INFLUXDB_TOKEN')
# url = os.getenv('INFLUXDB_URL')
token = "DVQEKd4L1iOek1bX5RmiXsIEGPYQnnYYUP6RLO5Wk-OwhBLjWc04qnD7AtYXNtlgJxTI4UUVdR7OyxTZEfqMiQ=="
url = "http://172.19.0.2:8086"
org = "SIUE SOLAR RACING TEAM"
bucket = "LogData"


client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

InfluxLoader = InfluxCANTools(write_api, "BMS.dbc", bucket, org)

dbcfiles = ['BMS.dbc', 'can9-database-01.09.dbc']
InfluxLoader.database(dbcfiles)

# Open log file
with can.LogReader("00000001.mf4") as reader:

    # Read messages
    for msg in reader:
        # print(msg)
        # print(msg.arbitration_id)
        InfluxLoader.UploadMessageToInflux(msg)

while True:
    time.sleep(1)
