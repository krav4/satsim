import socket
import time
from ccsds import *

udp_ip = "192.168.1.154"
udp_port = 8080

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in xrange(0, len(lst), n):
        yield lst[i:i + n]

f = open("datahawk_dave.jpeg", "rb")
bitstream = f.read()

payload_size = 512 #bytes - size of CCSDS payload
apid = "00000100001" #apid - depends on application
pkt_sequence_count = 0

chunked_bitstream = list(chunks(bitstream, payload_size))
print("%i chunks in bitstream, last chunk is %i bytes" % (len(chunked_bitstream), len(chunked_bitstream[-1]))) 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto("txstart", (udp_ip, udp_port))


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
		pkt_type=b"0",
		sec_flag=b"0",
		apid=apid,
		payload=bytearray(chunk),
		sequence_flags=sequence_flag,
		pkt_sequence_count=pkt_sequence_count
	)
	###################################

	print("Sending packet %i out of %i" %(i, len(chunked_bitstream)))
	print(pkt.show_primary_header())
	print(type(pkt.primary_header_binary))
	s.sendto(pkt.binary, (udp_ip, udp_port))
	pkt_sequence_count += 1
	time.sleep(0.07)
s.sendto("txend", (udp_ip, udp_port))

s.close()
