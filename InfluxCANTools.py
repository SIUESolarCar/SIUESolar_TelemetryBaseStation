import cantools
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os


class InfluxCANTools:
    ''' A class for handling InfluxDB operations with CAN messages.'''

    def __init__(self, write_api, DBCfile, bucket, org):
        self.write_api = write_api
        self.db = cantools.database.load_file(DBCfile)
        self.bucket = bucket
        self.org = org
        self.FrameIdList = self.FrameIdList(self.db)

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

    def FrameName(self, frame):
        FrameID = frame['id']
        return(FrameID)

    def DecodeMessage(self, db, frame):
        message = db.decode_message(frame['id'], self.ConvertHexDataToBytes(f))
        return(message)

    def FrameIdList(self, db):
        '''
        Function to append all the FrameIds from a db to a frame id list
        '''

        FrameIdList = []

        dbc_length = len(db._messages)

        for index in range(dbc_length):
            frame_id_hex = db._messages[index].frame_id
            FrameIdList.append(frame_id_hex)

        return FrameIdList

    def UploadMessageToInflux(self, frame):
        '''
        Function that takes the can message and uploads it to the database
        '''

        frame_name = self.FrameName(frame)
        
        if frame_name not in self.FrameIdList(self.db):
            return -1

        message = self.DecodeMessage(self.db, frame)

        keys_list = list(message.keys())

        record = influxdb_client.Point(frame_name)
        for datapoints in range(len(message)):
            record = record.field(keys_list[datapoints], message[keys_list[datapoints]])

        try:
            self.write_api.write(self.bucket, self.org, record)
            return 1
        except:
            return -1