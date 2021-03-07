from bitstring import BitArray

def build_binary(field_list):
	out = ''
	for field in field_list:
		out += field
	return BitArray(bin=out)

class PacketIdentification:
	def __init__(self, pkt_type, sec_flag, apid):
		assert len(pkt_type) == 1
		assert len(sec_flag) == 1
		assert len(apid) == 11
		self.pkt_type = pkt_type
		self.sec_flag = sec_flag
		self.apid = apid

		
	def to_list(self):
		return [self.pkt_type, self.sec_flag, self.apid]

class PacketSequenceControl:
	def __init__(self, sequence_flags=None, pkt_sequence_count=None):
		self.sequence_flags = sequence_flags
		
		if self.sequence_flags is None:
			self.sequence_flags = '11'
		else:
			try:
				assert len(self.sequence_flags) == 2
			except AssertionError:
				if self.sequence_flags == "first":
					self.sequence_flags = "01"
				elif self.sequence_flags == "continue":
					self.sequence_flags = "00"
				elif self.sequence_flags == "last":
					self.sequence_flags = "10"
				else:
					raise AssertionError("invalid sequence flag")
		
		if pkt_sequence_count is None:
			self.pkt_sequence_count = BitArray(uint=0, length=14).bin
		else:
			self.pkt_sequence_count = BitArray(uint=pkt_sequence_count, length=14).bin
	
	def to_list(self):
		return [self.sequence_flags, self.pkt_sequence_count]
	
class PacketDataLength:
	def __init__(self, number_of_bytes):
		assert number_of_bytes % 2 == 0
		number_of_octets = number_of_bytes/2
		self.pkt_data_length = BitArray(uint = number_of_octets - 1, length=16).bin
	def to_list(self):
		return [self.pkt_data_length]

class PrimaryHeader:
	def __init__(self, pkt_identification, pkt_sequence_control, pkt_data_length, pkt_version=None):
		if pkt_version is None:
			self.pkt_version = '010'
		self.pkt_identification = pkt_identification
		self.pkt_sequence_control = pkt_sequence_control
		self.pkt_data_length = pkt_data_length
	def primary_header_as_list(self):
		return [self.pkt_version] + self.pkt_identification.to_list() + self.pkt_sequence_control.to_list() + self.pkt_data_length.to_list()

class Packet(PrimaryHeader):
	def __init__(self, pkt_identification, pkt_sequence_control, payload, pkt_version=None):
		number_of_bytes = len(payload)
		pkt_data_length = PacketDataLength(number_of_bytes)
		PrimaryHeader.__init__(self, pkt_identification, pkt_sequence_control, pkt_data_length, pkt_version=None)
		self.payload = payload
		
		self.primary_header_binary = build_binary(self.primary_header_as_list())
		self.binary = self.primary_header_binary + payload

		
pkt_identification = PacketIdentification("0", "0", "00000000001")
pkt_sequence_control = PacketSequenceControl(sequence_flags=None, pkt_sequence_count=13)
pkt = Packet(pkt_identification, pkt_sequence_control, payload = BitArray(bin="1111"))
print pkt.binary, pkt.primary_header_as_list()

