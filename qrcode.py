# todo: @feature support model 1
# todo: @feature support frame qr
# todo: @dev put steps into seperate functions

from enum import Enum
from capacities_table import CAPACITIES
from codewords_table import CODEWORDS
import error_correction
from error_correction import Polynomial, ComplexCoefficent
from util import exponent_to_int, int_to_exponent


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

class QRCode:

	def __init__(self, data, error_correction=ERROR_CORRECTION.M):
		'''
		support string data only for now,
		todo: @feature should support more types in the furture.
		'''
		self.data = data
		self.error_correction = error_correction


	def generate(self):
		data = self.encode_data(self.data)
		# print(' '.join(data))
		self.generate_error_correction_codewords(data)

	def encode_data(self, data):
		error_correction = self.error_correction
		mode = self.determine_mode(data)
		version = self.determine_version(data, mode, error_correction)
		self.mode = mode
		self.version = version
		bit_data = self.get_bit_data(data, mode, version, error_correction)
		return [bit_data[i:i+8] for i in range(0, len(bit_data), 8)]


	def determine_mode(self, data):
		if data.isdigit():
			return DATA_MODE.NUMERIC
		elif all(char in ALNUM for char in data):
			return DATA_MODE.ALPHANUMERIC
		return DATA_MODE.BYTE

	def determine_version(self, data, mode, ec):
		version = 1
		capacity = CAPACITIES[mode.value][ec.value][version-1]
		while(len(data) > capacity):
			version += 1
			capacity = CAPACITIES[mode.value][ec.value][version-1]
		return version

	def get_bit_data(self, data, mode, version, error_correction):
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

		mode_indicator = self.get_mode_indicator(mode)
		count_indicator = self.get_count_indicator(data, mode, version)
		bit_data = mode_indicator + count_indicator + bit_data
		bit_data = self.add_pads(bit_data, version, error_correction)
		return bit_data


	def get_mode_indicator(self, mode):
		if mode == DATA_MODE.NUMERIC:
			return '0001'
		elif mode == DATA_MODE.ALPHANUMERIC:
			return '0010'
		else:
			return '0100'

	def get_count_indicator(self, data, mode, version):
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

	def add_pads(self, bit_data, version, error_correction):
		required_bits = CODEWORDS[error_correction.value][0][version-1] * 8
		bits_difference = required_bits - len(bit_data)
		if bits_difference > 4:
			bits_difference = 4
		bit_data += '0' * bits_difference
		if len(bit_data) % 8 != 0:
			bit_data += '0' * (8 - len(bit_data) % 8)
		required_pads = (required_bits - len(bit_data)) / 8
		for i in range(0, int(required_pads / 2)):
			bit_data += '1110110000010001'
		if required_pads % 2:
			bit_data += '11101100'
		return bit_data

	def generate_error_correction_codewords(self, data):
		ecc_len = CODEWORDS[self.error_correction.value][1][self.version-1]
		coefficients = list(map(lambda x: int(x, 2), data))

		generator_polynomial = error_correction.get_generator_polynomial(ecc_len)
		message_polynomial = error_correction.get_message_polynomial(coefficients)

		generator_polynomial = generator_polynomial.multiplyByExponent(len(data)-1)
		message_polynomial = message_polynomial.multiplyByExponent(ecc_len)
		print("Message Polynomial:")
		print(message_polynomial)

		# Multiply the generator polynomial by the lead term of the message polynomial
		leading_coefficient = coefficients[0]
		exponent = error_correction.int_to_exponent(leading_coefficient)
		generator_polynomial = \
			generator_polynomial.multiply(Polynomial(ComplexCoefficent(exponent)))
		generator_polynomial_int = generator_polynomial.get_int_form()
		print("Generator Polynomial (int form):")
		print(generator_polynomial_int)
		result = message_polynomial.XOR(generator_polynomial_int)
		print("XOR Result:")
		print(result)
		print(int_to_exponent(result.terms[0].coefficient))