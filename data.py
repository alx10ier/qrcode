from capacities_table import CAPACITIES
from codewords_table import CODEWORDS
from enum import Enum

class DATA_MODE(Enum):
	NUMERIC = 0
	ALPHANUMERIC = 1
	BYTE = 2
	KANJI = 3

class ERROR_CORRECTION(Enum):
	L = 0
	M = 1
	Q = 2
	H = 3

ALNUM = ('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:')
REMAINDER_BITS = [0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0]

def get_final_message(dc, ecc, ec, version):
	# interleave the data codewords
	interleaved_dc = []
	num_blocks_group_1 = CODEWORDS[ec.value][2][version-1]
	num_blocks_group_2 = CODEWORDS[ec.value][4][version-1]
	num_dc_group_1 = CODEWORDS[ec.value][3][version-1]
	num_dc_group_2 = CODEWORDS[ec.value][5][version-1]

	for i in range(0, num_dc_group_1):
		for j in range(0, len(dc)):
			interleaved_dc.append(dc[j][i])

	for i in range(num_blocks_group_1, len(dc)):
		interleaved_dc.append(dc[i][-1])

	# interleave the error correction codewords
	interleave_ecc = []
	for i in range(0, len(ecc[0])):
		for j in range(0, len(ecc)):
			interleave_ecc.append(ecc[j][i])

	interleave_message = interleaved_dc + interleave_ecc
	final_message = "".join(["{:08b}".format(codeword) for codeword in interleave_message])
	final_message = final_message + '0' * REMAINDER_BITS[version-1]
	return(final_message)

def get_data_codewords(data, ec, mode, version):
	if mode == DATA_MODE.NUMERIC:
		data_groups = [data[i:i+3] for i in range(0, len(data), 3)]
		bit_groups = []
		for group in data_groups:
			if len(group) == 3:
				bit_groups.append('{:010b}'.format(int(group)))

			elif len(group) == 2:
				bit_groups.append('{:07b}'.format(int(group)))

			else:
				bit_groups.append('{:04b}'.format(int(group)))
	elif mode == DATA_MODE.ALPHANUMERIC:
		data_groups = [data[i:i+2] for i in range(0, len(data), 2)]
		bit_groups = []
		for i in range(0, len(data_groups)):
			group = data_groups[i]
			if len(group) == 1:
				value = ALNUM.index(group[0])
				bit_groups.append(format(value, '06b'))
			if len(group) == 2:
				value = ALNUM.index(group[0]) * 45 + ALNUM.index(group[1])
				bit_groups.append(format(value, '011b'))
	else:
		bit_groups = ["{:08b}".format(c) for c in data.encode('iso-8859-1')]
	bit_data = ''.join(bit_groups)

	mode_indicator = get_mode_indicator(mode)
	count_indicator = get_count_indicator(data, mode, version)
	bit_data = mode_indicator + count_indicator + bit_data
	bit_data = add_pads(bit_data, version, ec)
	bit_data = [bit_data[i:i+8] for i in range(0, len(bit_data), 8)]
	
	data_codewords = list(map(lambda x: int(x, 2), bit_data))

	# group data_codewords
	blocks = []
	num_blocks_group_1 = CODEWORDS[ec.value][2][version-1]
	num_blocks_group_2 = CODEWORDS[ec.value][4][version-1]
	num_dc_group_1 = CODEWORDS[ec.value][3][version-1]
	num_dc_group_2 = CODEWORDS[ec.value][5][version-1]
	total_dc_group_1 = num_blocks_group_1 * num_dc_group_1
	for i in range(0, num_blocks_group_1):
		blocks.append(data_codewords[i*num_dc_group_1:(i+1)*num_dc_group_1])
	for i in range(0, num_blocks_group_2):
		blocks.append(data_codewords[total_dc_group_1+i*num_dc_group_2:total_dc_group_1+(i+1)*num_dc_group_2])
	return blocks

def determine_mode(data):
	if data.isdigit():
		return DATA_MODE.NUMERIC
	elif all(char in ALNUM for char in data):
		return DATA_MODE.ALPHANUMERIC
	return DATA_MODE.BYTE

def determine_version(data, ec, mode):
	version = 1
	capacity = CAPACITIES[mode.value][ec.value][version-1]
	while(len(data) > capacity):
		version += 1
		capacity = CAPACITIES[mode.value][ec.value][version-1]
	return version

def get_mode_indicator(mode):
		if mode == DATA_MODE.NUMERIC:
			return '0001'
		elif mode == DATA_MODE.ALPHANUMERIC:
			return '0010'
		else:
			return '0100'

def get_count_indicator(data, mode, version):
	if mode == DATA_MODE.NUMERIC:
		if 1 <= version <=9:
			count_indicator_len = 10
		elif 10 <= version <= 26:
			count_indicator_len = 12
		else:
			count_indicator_len = 14
	elif mode == DATA_MODE.ALPHANUMERIC:
		if 1 <= version <=9:
			count_indicator_len = 9
		elif 10 <= version <= 26:
			count_indicator_len = 11
		else:
			count_indicator_len = 13
	else:
		if 1 <= version <=9:
			count_indicator_len = 8
		elif 10 <= version <= 26:
			count_indicator_len = 16
		else:
			count_indicator_len = 16
	return '{num:0{width}b}'.format(num=len(data), width=count_indicator_len)

def add_pads(data, version, ec):
		required_bits = CODEWORDS[ec.value][0][version-1] * 8
		bits_difference = required_bits - len(data)
		if bits_difference > 4:
			bits_difference = 4
		data += '0' * bits_difference
		if len(data) % 8 != 0:
			data += '0' * (8 - len(data) % 8)
		required_pads = (required_bits - len(data)) / 8
		for i in range(0, int(required_pads / 2)):
			data += '1110110000010001'
		if required_pads % 2:
			data += '11101100'
		return data
