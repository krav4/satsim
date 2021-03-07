from bitstring import BitArray

def getbytes(bits):
    done = False
    while not done:
        byte = 0
        for _ in range(0, 8):
            try:
                bit = next(bits)
            except StopIteration:
                bit = 0
                done = True
            byte = (byte << 1) | int(bit)
        yield byte
        
def build_binary(field_list):
	bits = b""
	for field in field_list:
		bits += field
	out = None
	for byte in getbytes(iter(bits)):
		out += byte
	return out

class PacketIdentification:
	def __init__(self, pkt_type, sec_flag, apid):
		assert len(pkt_type) == 1
		assert len(sec_flag) == 1
		assert len(apid) == 11
		self.pkt_type = pkt_type
		self.sec_flag = sec_flag
		self.apid = apid
		

class PacketSequenceControl:
	def __init__(self, sequence_flags=None, pkt_sequence_count=None):
		self.sequence_flags = sequence_flags
		
		if self.sequence_flags is None:
			self.sequence_flags = b'11'
		else:
			try:
				assert len(self.sequence_flags) == 2
			except AssertionError:
				if self.sequence_flags == "first":
					self.sequence_flags = b"01"
				elif self.sequence_flags == "continue":
					self.sequence_flags = b"00"
				elif self.sequence_flags == "last":
					self.sequence_flags = b"10"
				else:
					raise AssertionError("invalid sequence flag")
		
		if pkt_sequence_count is None:
			self.pkt_sequence_count = BitArray(uint=0, length=14).bin
		else:
			self.pkt_sequence_count = BitArray(uint=pkt_sequence_count, length=14).bin
	
class PacketDataLength:
	def __init__(self, number_of_bytes):
		number_of_octets = int(number_of_bytes/2)
		self.pkt_data_length = BitArray(uint = number_of_octets - 1, length=16).bin


class PrimaryHeader(PacketIdentification, PacketSequenceControl, PacketDataLength):
	def __init__(self, pkt_type, sec_flag, apid, num_bytes, sequence_flags=None, pkt_sequence_count=None, pkt_version=None):
		PacketIdentification.__init__(self, pkt_type, sec_flag, apid)
		PacketSequenceControl.__init__(self, sequence_flags, pkt_sequence_count)
		PacketDataLength.__init__(self, num_bytes)
		if pkt_version is None:
			self.pkt_version = b'010'
	def primary_header_as_list(self):
		return [self.pkt_version, self.pkt_type, self.sec_flag, self.apid, self.sequence_flags, self.pkt_sequence_count, self.pkt_data_length]
	def show_primary_header(self):
		return {
			"pkt_version": self.pkt_version,
			"pkt_type": self.pkt_type,
			"secondary_header_flag": self.sec_flag,
			"apid": self.apid,
			"sequence_flag": self.sequence_flags,
			"sequence_count": self.pkt_sequence_count,
			"user_data_length": self.pkt_data_length
		}

class Packet(PrimaryHeader):
	def __init__(self, pkt_type, sec_flag, apid, payload, sequence_flags=None, pkt_sequence_count=None, pkt_version=None):
		self.payload = payload
		num_bytes = len(payload)
		
		PrimaryHeader.__init__(self, pkt_type, sec_flag, apid, num_bytes, sequence_flags, pkt_sequence_count, pkt_version)
		
		self.primary_header_binary = build_binary(self.primary_header_as_list())
		self.binary = self.primary_header_binary + self.payload
