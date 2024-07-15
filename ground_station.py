import socket
import itertools
import time
from datetime import datetime
from bitstring import BitArray
from ccsds import unpack
from pprint import pprint
import signal
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ip", help="ip address of the satellite", type=str, default='127.0.0.1')
parser.add_argument("--port", help="port to bind for satellite", type=int, default=8080)
parser.add_argument("--out", help="output filename for received imagery", type=str, default="received_imagery.jpeg")
args = parser.parse_args()

signal.signal(signal.SIGINT, signal.SIG_DFL)
print("Creating a UDP socket")
serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Binding to the Ground Station UDP/IP address and port: %s:%s" % (args.ip,  args.port))
serversocket.bind((args.ip, args.port))

transmission_report = open("transmission_report.txt", "a")
while True:
    try:
        data, address = serversocket.recvfrom(512+48)
        if data.decode('utf-8', errors="ignore") == "txstart":
            print("Imagery transmission started")
            count=0
            image = b''
        elif data.decode('utf-8', errors="ignore") == "txend":
            print("Imagery transmission finished")
            if image:
                with open(args.out, "wb") as f:
                    f.write(image)
                print("Imagery written to a file")
            else:
                print("Received imagery is empty")
            count = 0
        else:
            print("Received packet %i of imagery transmission" % count)
            count += 1
            mapped_header = unpack(data, header_length=6)
            print(mapped_header)
            transmission_report.write(str(datetime.utcnow()) + " : " + str(mapped_header) + "\n")
            transmission_report.flush()
            image += data[6:]
        time.sleep(0.01)
    except KeyboardInterrupt:
        transmission_report.close()
        break
