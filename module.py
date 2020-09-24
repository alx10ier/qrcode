from align_patterns_table import ALIGN_PATTERN_LOCATIONS
from data import ERROR_CORRECTION
from math import floor

def get_module_matrix(data, version, ec):
	matrix = Matrix((version-1)*4+21, (version-1)*4+21)

	# add finder patterns
	finder_pattern = generate_finder_pattern()
	matrix.add(finder_pattern)
	matrix.add(finder_pattern, 0, matrix.width-7)
	matrix.add(finder_pattern, matrix.height-7, 0)

	# add seperators
	matrix.fill_row(7, range(0, 8), 'w')
	matrix.fill_col(7, range(0, 7), 'w')
	matrix.fill_row(7, range(matrix.width-8, matrix.width), 'w')
	matrix.fill_col(matrix.width-8, range(0, 7), 'w')
	matrix.fill_row(matrix.height-8, range(0, 8), 'w')
	matrix.fill_col(7, range(matrix.height-8, matrix.height), 'w')

	# add aligh patterns
	positions = get_align_pattern_positions(version)
	align_pattern = generate_align_pattern()
	for position in positions:
		matrix.add(align_pattern, *position)

	# add timing patterns
	matrix.fill_col(6, color='w', cover=False)
	matrix.fill_row(6, color='w', cover=False)
	for i in range(8, matrix.width-8, 2):
		matrix.fill_module(i, 6)
		matrix.fill_module(6, i)

	# add dark module
	matrix.fill_module(version*4+9, 8)

	# reserve format information area
	matrix.fill_row(8, range(0, 9), color='r', cover=False)
	matrix.fill_col(8, range(0, 8), color='r', cover=False)
	matrix.fill_row(8, range(matrix.width-8, matrix.width), color='r', cover=False)
	matrix.fill_col(8, range(matrix.height-8, matrix.width), color='r', cover=False)

	# reserve version information area
	if version >= 7:
		for i in range(0, 3):
			matrix.fill_row(matrix.height-9-i, range(0, 6), color='r')
		for i in range(0, 3):
			matrix.fill_col(matrix.width-9-i, range(0, 6), color='r')

	# get reference matrix
	reference_matrix = []
	for i in range(0, matrix.height):
			reference_matrix.append([])
			for j in range(0, matrix.width):
				reference_matrix[i].append(None)

	for i in range(0, len(matrix.modules)):
		for j in range(0, len(matrix.modules[0])):
			reference_matrix[i][j] = 1 if matrix.get_module(i, j) is None else 0

	# place data bits
	place_data_bits(matrix, data)

	# choose best mask pattern
	scores = []
	matrices = []
	for i in range(0, 8):
		test_matrix = mask(matrix.modules, reference_matrix, i)
		add_information(test_matrix, ec, i, version)
		scores.append(get_score(test_matrix))
		matrices.append(test_matrix)
	return matrices[scores.index(min(scores))].modules

def get_score(matrix):
	row_modules = matrix.modules
	penalty = 0
	col_modules = [[] for row in row_modules]
	for row in row_modules:
		for i, module in enumerate(row):
			col_modules[i].append(module)

	# condition 1
	penalty += check_condition_1(row_modules)
	penalty += check_condition_1(col_modules)

	# condition 2
	penalty += check_condition_2(row_modules)

	# condition 3
	penalty += check_condition_3(row_modules)
	penalty += check_condition_3(col_modules)

	# condition 4
	penalty ++ check_condition_4(row_modules)

	return penalty

def check_condition_1(modules):
	penalty = 0
	for row in modules:
		i = 1;
		test_array = [row[0]]
		while i < len(row):
			module = row[i]
			if module != test_array[0]:
				if len(test_array) >= 5:
					penalty += len(test_array)-2 
				test_array = []
			test_array.append(module)
			i += 1
		else:
			if len(test_array) >= 5:
					penalty += len(test_array)-2 
	return penalty

def check_condition_2(modules):
	penalty = 0
	for i in range(0, len(modules)-1):
		for j in range(0, len(modules[0])-1):
			if modules[i][j] == modules[i+1][j] == modules[i][j+1] == modules[i+1][j+1]:
				penalty += 3
	return penalty

def check_condition_3(modules):
	penalty = 0
	pattern_1 = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0]
	pattern_2 = list(reversed(pattern_1))
	for row in modules:
		for i in range(0, len(row)-10):
			section = row[i:i+11]
			if section == pattern_1 or section == pattern_2:
				penalty += 40
	return penalty

def check_condition_4(modules):
	module_count = 0
	dark_count = 0
	for row in modules:
		for module in row:
			module_count += 1
			if module == 1: dark_count += 1
	percent = dark_count/module_count*100
	lower = 5*floor(percent/5)
	higher = lower + 5
	return min(abs(lower-50)/5, abs(higher-50)/5)
		
def mask(matrix, reference, type):
	pattern_0 = lambda x, y: not (x+y)%2
	pattern_1 = lambda x, y: not x%2
	pattern_2 = lambda x, y: not y%3
	pattern_3 = lambda x, y: not (x+y)%3
	pattern_4 = lambda x, y: not (floor(x/2)+floor(y/3))%2
	pattern_5 = lambda x, y: not ((x*y)%2)+((x*y)%3)
	pattern_6 = lambda x, y: not (((x*y)%2)+((x*y)%3))%2
	pattern_7 = lambda x, y: not (((x+y)%2)+((x*y)%3))%2

	if type == 0: pattern = pattern_0
	elif type == 1: pattern = pattern_1
	elif type == 2: pattern = pattern_2
	elif type == 3: pattern = pattern_3
	elif type == 4: pattern = pattern_4
	elif type == 5: pattern = pattern_5
	elif type == 6: pattern = pattern_6
	elif type == 7: pattern = pattern_7 

	modules = []
	for row in matrix:
		modules.append(row.copy())

	for i in range(0, len(matrix)):
		for j in range(0, len(matrix[0])):
			if pattern(i, j) and reference[i][j]:
				module = matrix[i][j]
				module = 1 if module == 0 else 0
				modules[i][j] = module

	matrix = Matrix()
	matrix.modules = modules
	return matrix

def add_information(matrix, ec, pattern_num, version):
	# add format information
	format_string = ""
	generator_string = "10100110111"
	mask_string = "101010000010010"

	if ec == ERROR_CORRECTION.L: format_string += "01"
	elif ec == ERROR_CORRECTION.M: format_string += "00"
	elif ec == ERROR_CORRECTION.Q: format_string += "11"
	elif ec == ERROR_CORRECTION.H: format_string += "10"

	format_string += "{:03b}".format(pattern_num)
	ec_string = format_string + "0"*10
	while len(ec_string) and ec_string[0] == "0":
		ec_string = ec_string[1:]
	while len(ec_string) > 10:
		generator_string_current = generator_string + "0"*(len(ec_string)-len(generator_string))
		result = int(ec_string, 2) ^ int(generator_string_current, 2)
		ec_string = '{:b}'.format(result)
	ec_string = "0"*(10-len(ec_string)) + ec_string
	result = int(format_string + ec_string, 2) ^ int(mask_string, 2)
	format_string = '{:b}'.format(result)
	format_string = "0"*(15-len(format_string)) + format_string

	format_modules = ['b' if bit == '1' else 'w' for bit in format_string]
	for i in range(0, 6):
		matrix.fill_module(8, i, format_modules[i])
	for i in range(6, 8):
		matrix.fill_module(8, i+1, format_modules[i])
	matrix.fill_module(7, 8, format_modules[8])
	for i in range(9, 15):
		matrix.fill_module(14-i, 8, format_modules[i])
	for i in range(0, 7):
		matrix.fill_module(matrix.height-1-i, 8, format_modules[i])
	for i in range(7, 15):
		matrix.fill_module(8, matrix.width-1-(14-i), format_modules[i])

	# add version information
	if (version < 7): return
	generator_string = "1111100100101"
	version_string = "{:06b}".format(version)
	ec_string = version_string + "0"*12
	while ec_string[0] == "0":
		ec_string = ec_string[1:]
	while len(ec_string) > 12:
		generator_string_current = generator_string + "0"*(len(ec_string)-len(generator_string))
		result = int(ec_string, 2) ^ int(generator_string_current, 2)
		ec_string = '{:b}'.format(result)
	ec_string = "0"*(12-len(ec_string)) + ec_string
	version_string = version_string + ec_string
	version_string = version_string[::-1]

	version_modules = ['b' if bit == '1' else 'w' for bit in version_string]
	for i in range(0, 6):
		for j in range(0, 3):
			matrix.fill_module(matrix.height-11+j, i, version_modules[i*3+j])
	for i in range(0, 6):
		for j in range(0, 3):
			matrix.fill_module(i, matrix.width-11+j, version_modules[i*3+j])

def place_data_bits(matrix, data):
	up = True
	left = True
	up_stop = True
	current_position = (matrix.height-1, matrix.width-1)
	i = 0
	while i < len(data):
		pass
		color = 'b' if data[i] == '1' else 'w'

		if matrix.get_module(*current_position) is None:
			matrix.fill_module(*current_position, color)
		else:
			i -= 1

		# get next position
		col_shift = 0
		if not up_stop:
			new_row = current_position[0]-1 if up else current_position[0]+1
			if new_row not in range(0, matrix.height):
				new_row = current_position[0]
				up = not up
				col_shift -= 2
		else:
			new_row = current_position[0]
		
		new_col = current_position[1]-1 if left else current_position[1]+1
		new_col += col_shift
		if col_shift and new_col == 6: new_col -= 1


		left = not left
		up_stop = not up_stop

		current_position = (new_row, new_col)
		i += 1

def generate_finder_pattern():
	matrix = Matrix(7, 7)
	matrix.fill_all()
	matrix.fill_row(1, range(1, 6), 'w')
	matrix.fill_row(5, range(1, 6), 'w')
	matrix.fill_col(1, range(2, 5), 'w')
	matrix.fill_col(5, range(2, 5), 'w')
	return matrix.modules

def generate_align_pattern():
	matrix = Matrix(5, 5)
	matrix.fill_all()
	matrix.fill_row(1, range(1, 4), 'w')
	matrix.fill_row(3, range(1, 4), 'w')
	matrix.fill_module(2, 1, 'w')
	matrix.fill_module(2, 3, 'w')
	return matrix.modules

def get_align_pattern_positions(version):
	if version < 2:
		return []
	positions = []
	anchors = ALIGN_PATTERN_LOCATIONS[version-2]
	for anchor_1 in anchors:
		for anchor_2 in anchors:
			positions.append((anchor_1-2, anchor_2-2))

	# remove 3 align patterns that overlap with finder patterns
	positions.remove((anchors[0]-2, anchors[0]-2))
	positions.remove((anchors[0]-2, anchors[-1]-2))
	positions.remove((anchors[-1]-2, anchors[0]-2))
	return positions


class Matrix:
	def __init__(self, width=0, height=0):
		self.modules = []
		self.width = width
		self.height = height
		for i in range(0, height):
			self.modules.append([])
			for j in range(0, width):
				self.modules[i].append(None)

	def add(self, matrix, start_row=0, start_col=0):
		if isinstance(matrix, Matrix):
			matrix = matrix.modules
		for i in range(0, len(matrix)):
			for j in range(0, len(matrix[0])):
				self.modules[start_row+i][start_col+j] = matrix[i][j]

	def get_module(self, row, col):
		return self.modules[row][col]

	def fill_module(self, row, col, color='b', cover=True):
		if color == 'w':
			mark = 0
		elif color == 'b':
			mark = 1
		else:
			mark = 2

		if not cover and self.modules[row][col] is not None:
			return

		self.modules[row][col] = mark


	def fill_row(self, row, row_range=None, color='b', cover=True):
		if row_range:
			for i in row_range:
				self.fill_module(row, i, color, cover)
		else:
			for i in range(0, len(self.modules[row])):
				self.fill_module(row, i, color, cover)

	def fill_col(self, col, col_range=None, color='b', cover=True):
		if col_range:
			for i in col_range:
				self.fill_module(i, col, color, cover)
		else:
			for i in range(0, len(self.modules)):
				self.fill_module(i, col, color, cover)

	def fill_all(self, color='b', cover=True):
		for i in range(0, len(self.modules)):
			for j in range(0, len(self.modules[0])):
				self.fill_module(i, j, color, cover)