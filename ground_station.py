import socket
import itertools
import time
from bitstring import BitArray
print("Creating a UDP socket")
serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Binding to the Ground Station UDP/IP address and port: %s:%s" % (str(socket.gethostname()), "8080"))
serversocket.bind((socket.gethostname(), 8080))


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
                with open("received_imagery.jpeg", "wb") as f:
                    f.write(image)
                print("Imagery written to a file")
            else:
                print("Received imagery is empty")
            count = 0
        else:
            print("Received packet %i of imagery transmission" % count)
            count += 1
            primary_header=data[0:6]
            print(BitArray().frombytes(primary_header))
            image += data[6:]
        time.sleep(0.01)
    except KeyboardInterrupt:
        break
