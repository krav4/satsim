from bitstring import BitArray
import bitarray
from collections import OrderedDict

field_length_mapping = OrderedDict([
	("pkt_version", 3),
	("pkt_type", 1),
	("secondary_header_flag", 1),
	("apid", 11),
	("sequence_flag", 2),
	("sequence_count", 14),
	("user_data_length", 16)
])

def build_binary(field_list):
	ba = bitarray.bitarray()
	# for field in field_list:
	ba.extend("".join(field_list))
	out = ba.tobytes()
	return out

class PacketIdentification:
	def __init__(self, pkt_type, sec_flag, apid):
		assert len(pkt_type) == field_length_mapping["pkt_type"]
		assert len(sec_flag) == field_length_mapping["secondary_header_flag"]
		assert len(apid) == field_length_mapping["apid"]
		self.pkt_type = pkt_type
		self.sec_flag = sec_flag
		self.apid = apid


class PacketSequenceControl:
	def __init__(self, sequence_flags=None, pkt_sequence_count=None):
		self.sequence_flags = sequence_flags

		if self.sequence_flags is None:
			self.sequence_flags = "11"
		else:
			try:
				assert len(self.sequence_flags) == field_length_mapping["sequence_flag"]
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
			self.pkt_sequence_count = BitArray(uint=0, length=field_length_mapping["sequence_count"]).bin
		else:
			self.pkt_sequence_count = BitArray(uint=pkt_sequence_count, length=field_length_mapping["sequence_count"]).bin

class PacketDataLength:
	def __init__(self, number_of_bytes):
		number_of_octets = int(number_of_bytes/2)
		self.pkt_data_length = BitArray(uint = number_of_octets - 1, length=field_length_mapping["user_data_length"]).bin


class PrimaryHeader(PacketIdentification, PacketSequenceControl, PacketDataLength):
	def __init__(self, pkt_type, sec_flag, apid, num_bytes, sequence_flags=None, pkt_sequence_count=None, pkt_version=None):
		PacketIdentification.__init__(self, pkt_type, sec_flag, apid)
		PacketSequenceControl.__init__(self, sequence_flags, pkt_sequence_count)
		PacketDataLength.__init__(self, num_bytes)
		if pkt_version is None:
			self.pkt_version = "010"
	def primary_header_as_list(self):
		return [self.pkt_version, self.pkt_type, self.sec_flag, self.apid, self.sequence_flags, self.pkt_sequence_count, self.pkt_data_length]
	def show_primary_header(self):
		return OrderedDict([
			("pkt_version", self.pkt_version),
			("pkt_type", self.pkt_type),
			("secondary_header_flag", self.sec_flag),
			("apid", self.apid),
			("sequence_flag", self.sequence_flags),
			("sequence_count", self.pkt_sequence_count),
			("user_data_length", self.pkt_data_length)
		])

class Packet(PrimaryHeader):
	def __init__(self, pkt_type, sec_flag, apid, payload, sequence_flags=None, pkt_sequence_count=None, pkt_version=None):
		self.payload = payload
		num_bytes = len(payload)

		PrimaryHeader.__init__(self, pkt_type, sec_flag, apid, num_bytes, sequence_flags, pkt_sequence_count, pkt_version)
		print(self.primary_header_as_list())
		self.primary_header_binary = build_binary(self.primary_header_as_list())
		self.binary = self.primary_header_binary + self.payload

def unpack(pkt_bin, header_length=6):
	ba = bitarray.bitarray()
	header_bytes = pkt_bin[0:header_length]
	ba.frombytes(header_bytes)
	header_binary = ba.to01()
	# ~ print(header_binary)
	mapped_header = OrderedDict([(k,None) for k, v in field_length_mapping.items()])

	previous_length = 0
	current_length = 0
	for idx, (field_name, length) in enumerate(field_length_mapping.items()):
		if idx == 0:
			pass
		else:
			previous_length += list(field_length_mapping.items())[idx-1][1]
		current_length += length
		mapped_header[field_name] = header_binary[previous_length:current_length]
	return mapped_header
