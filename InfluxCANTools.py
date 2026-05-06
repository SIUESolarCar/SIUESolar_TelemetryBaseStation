import cantools
import can
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from datetime import datetime, timezone


class InfluxCANTools:
    ''' A class for handling InfluxDB operations with CAN messages.'''

    def __init__(self, write_api, DBCfile, bucket, org):
        self.write_api = write_api
        self.bucket = bucket
        self.org = org

    def database(self, DBCfiles):
        self.db = cantools.database.Database()
        for dbcfile in DBCfiles:
            self.db.add_dbc_file(dbcfile)


    def ConvertHexDataToBytes(self, frame):
        # Makes list of hex from frame for conversion
        HexDataList = [
            hex(frame['data'][0]),
            hex(frame['data'][1]),
            hex(frame['data'][2]),
            hex(frame['data'][3]),
            hex(frame['data'][4]),
            hex(frame['data'][5]),
            hex(frame['data'][6]),
            hex(frame['data'][7])
            ]
        # Concatenate the hexadecimal strings together into one string
        CombinedHex = ''.join(DataPoint[2:].zfill(2) for DataPoint in HexDataList)
        # Convert the combined hexadecimal string into bytes
        CombinedBytes = bytes.fromhex(CombinedHex)
        return(CombinedBytes)

    def UploadFrameToInflux(self, frame):
        '''
        Function that takes the cantools frame and uploads it to the database
        '''
        
        if frame['id'] not in self.FrameIdList(self.db):
            return -1

        decoded = self.db.decode_message(frame['id'], self.ConvertHexDataToBytes(frame))

        keys_list = list(decoded.keys())

        record = influxdb_client.Point(frame['id'])
        for datapoints in range(len(decoded)):
            record = record.field(keys_list[datapoints], decoded[keys_list[datapoints]])

        try:
            self.write_api.write(self.bucket, self.org, record)
            return 1
        except:
            return -1
    
    def UploadMessageToInflux(self, msg):
        '''
        Function that takes the can message and uploads it to the database
        '''
        print("new message")
        try:
            decoded = self.db.decode_message(msg.arbitration_id, msg.data)

            print(f"ID {msg.arbitration_id}: {decoded}")

            keys_list = list(decoded.keys())

            dt = datetime.fromtimestamp(msg.timestamp, timezone.utc)
            rfc3339_string = dt.isoformat()


            point = influxdb_client.Point(msg.arbitration_id)
            for datapoints in range(len(decoded)):
                point = point.field(keys_list[datapoints], decoded[keys_list[datapoints]])
            point.time(rfc3339_string)

            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
        except Exception as e:
            print(f"An error occurred: {e}")
