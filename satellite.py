import socket
import time
import ccsdspy

udp_ip = "192.168.1.154"
udp_port = 8080

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in xrange(0, len(lst), n):
        yield lst[i:i + n]

f = open("datahawk_dave.jpeg", "rb")
bitstream = f.read()

payload_size = 512 #bytes - size of CCSDS payload

chunked_bitstream = list(chunks(bitstream, payload_size))
print("%i chunks in bitstream, last chunk is %i bytes" % (len(chunked_bitstream), len(chunked_bitstream[-1]))) 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto("txstart", (udp_ip, udp_port))
for i, chunk in enumerate(chunked_bitstream):
	print("Sending chunk %i out of %i" %(i, len(chunked_bitstream)))
	s.sendto(chunk, (udp_ip, udp_port))
	time.sleep(0.07)
s.sendto("txend", (udp_ip, udp_port))


s.close()
