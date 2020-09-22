from align_patterns_table import ALIGN_PATTERN_LOCATIONS
from math import floor

def get_module_matrix(data, version):
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

	#evaluate patterns
	# for i in range(0, 8):
	# 	masked_modules = mask(matrix.modules, reference_matrix, i)
	# 	score = get_score(masked_modules)

	matrix.modules = mask(matrix.modules, reference_matrix, 0)

	add_information(matrix)

	return matrix.modules

def get_score(modules):
	# penalty = 0
	# # condition 1
	# for row in modules:
	pass


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

	matrix_copy = []
	for row in matrix:
		matrix_copy.append(row.copy())

	for i in range(0, len(matrix)):
		for j in range(0, len(matrix[0])):
			if pattern(i, j) and reference[i][j]:
				module = matrix[i][j]
				module = 1 if module == 0 else 0
				matrix_copy[i][j] = module

	return matrix_copy

def add_information(matrix):
	information_bits = '011010101011111'
	information_modules = ['b' if bit == '1' else 'w' for bit in information_bits]
	for i in range(0, 6):
		matrix.fill_module(8, i, information_modules[i])
	for i in range(6, 8):
		matrix.fill_module(8, i+1, information_modules[i])
	matrix.fill_module(7, 8, information_modules[8])
	for i in range(9, 15):
		matrix.fill_module(14-i, 8, information_modules[i])
	for i in range(0, 7):
		matrix.fill_module(matrix.height-1-i, 8, information_modules[i])
	for i in range(7, 15):
		matrix.fill_module(8, matrix.width-1-(14-i), information_modules[i])

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
	def __init__(self, width, height):
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