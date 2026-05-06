import can
from datetime import datetime, timezone

# Open log file
with can.LogReader("00000001.mf4") as reader:

    # Read messages
    for msg in reader:
        dt = datetime.fromtimestamp(msg.timestamp, timezone.utc)
        rfc3339_string = dt.isoformat()
        print(rfc3339_string)



# import can
# import cantools

# db = cantools.database.load_file('car_data.dbc')
# bus = can.interface.Bus(channel='can0', bustype='socketcan')

# while True:
#     message = bus.recv() # Wait for a message
#     try:
#         # Match ID and decode
#         decoded = db.decode_message(message.arbitration_id, message.data)
#         # print(f"ID {message.arbitration_id}: {decoded}")
#         print(message.timestamp)
#     except KeyError:
#         # Message ID not in the DBC file
#         pass