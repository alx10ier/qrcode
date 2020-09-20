from tkinter import Tk, Frame, Canvas
from align_patterns_table import ALIGN_PATTERN_LOCATIONS

def get_module_matrix(version):
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
	for i in range(0, 3):
		matrix.fill_row(matrix.height-9-i, range(0, 6), color='r')
	for i in range(0, 3):
		matrix.fill_col(matrix.width-9-i, range(0, 6), color='r')

	# place data bits

	return matrix.modules


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
		return
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

class Example(Frame):
	def __init__(self):
		Frame.__init__(self)
		self.pack(fill='both', expand=1)

		self.canvas = Canvas(self, highlightthickness=0)
		self.canvas["background"] = '#666666'
		self.module_size = 10

	def draw(self, matrix):
		size = self.module_size
		for y, row in enumerate(matrix):
			for x, module in enumerate(row):
				if module == 1:
					self.canvas.create_rectangle(x*size, y*size, x*size+10, y*size+10, fill="black", outline="#333")
				elif module == 0:
					self.canvas.create_rectangle(x*size, y*size, x*size+10, y*size+10, fill="white", outline="#333")
				elif module == 2:
					self.canvas.create_rectangle(x*size, y*size, x*size+10, y*size+10, fill="blue", outline="#333")

				else:
					self.canvas.create_rectangle(x*size, y*size, x*size+10, y*size+10, outline="#333")


		self.canvas.pack(fill='both', expand=1)

	def set_module_size(size):
		self.module_size = size

def main():
	tk = Tk()
	ex = Example()
	ex.draw(get_module_matrix(8))
	tk.mainloop()

if __name__ == '__main__':
	main()