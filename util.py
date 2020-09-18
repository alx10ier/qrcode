from log_antilog_table import INTEGERS

def exponent_to_int(num):
		if num > 255:
			num %= 255
		return INTEGERS[num]

def int_to_exponent(num):
		return INTEGERS.index(num)