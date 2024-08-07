import socket
import time
from ccsds import *
from pprint import pprint
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ip", help="ip address of the ground station", type=str, default='127.0.0.1')
parser.add_argument("--port", help="port to bind for transmission", type=int, default=8080)
parser.add_argument("--transmit", help="file to transfer to the ground", type=str, default="satellite_imagery")
args = parser.parse_args()

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

f = open("satellite_imagery.jpeg", "rb")
bitstream = f.read()

payload_size = 512 #bytes - size of CCSDS payload
apid = "00000100001" #apid - depends on application
pkt_sequence_count = 0

chunked_bitstream = list(chunks(bitstream, payload_size))
print("%i chunks in bitstream, last chunk is %i bytes" % (len(chunked_bitstream), len(chunked_bitstream[-1]))) 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto("txstart".encode(), (args.ip, args.port))

for i, chunk in enumerate(chunked_bitstream):
	
	################################
	## ASSEMBLING PACKET###########
	if i == 0:
		sequence_flag = "first"
	elif i == len(chunked_bitstream) - 1:
		sequence_flag = "last"
	else:
		sequence_flag = "continue"
	
	pkt = Packet(
		pkt_type="0",
		sec_flag="0",
		apid=apid,
		payload=chunk,
		sequence_flags=sequence_flag,
		pkt_sequence_count=pkt_sequence_count
	)
	###################################

	print("Sending packet %i out of %i" %(i, len(chunked_bitstream)))
	print(pkt.show_primary_header())
	s.sendto(pkt.binary, (args.ip, args.port))
	pkt_sequence_count += 1
	time.sleep(0.01)
s.sendto("txend".encode(), (args.ip, args.port))

s.close()
