# -*- coding: UTF-8 -*-

from pprint import pprint
import qrcode 
from tkinter import Tk, Frame, Canvas

class Example(Frame):
	def __init__(self):
		Frame.__init__(self)
		self.pack(fill='both', expand=1)

		self.canvas = Canvas(self, highlightthickness=0)
		self.canvas["background"] = '#fff'
		self.module_size = 10

	def draw(self, matrix):
		size = self.module_size
		for y, row in enumerate(matrix):
			for x, module in enumerate(row):
				if module == 1:
					self.canvas.create_rectangle(4*size+x*size, 4*size+y*size, 4*size+x*size+10, 4*size+y*size+10, fill="black", outline="")
				elif module == 0:
					self.canvas.create_rectangle(4*size+x*size, 4*size+y*size, 4*size+x*size+10, 4*size+y*size+10, fill="white", outline="")
				elif module == 2:
					self.canvas.create_rectangle(4*size+x*size, 4*size+y*size, 4*size+x*size+10, 4*size+y*size+10, fill="blue", outline="")

				else:
					self.canvas.create_rectangle(4*size+x*size, 4*size+y*size, 4*size+x*size+10, 4*size+y*size+10, outline="#333")


		self.canvas.pack(fill='both', expand=1)

	def set_module_size(size):
		self.module_size = size

message_simple = 'HELLO WORLD'
message = 'This is the most important things that I have ever seen.'
message_cause_problem = 'This is the most important things that I have ever seen these days.'
message_that_is_really_long = 'This message is so long that ensure the version to be larger than 7, and I dont know what words to put inside of it.'


qr = qrcode.QRCode(message_simple, error_correction=qrcode.ERROR_CORRECTION.Q)
# qr = qrcode.QRCode(message, error_correction=qrcode.ERROR_CORRECTION.Q)
# qr = qrcode.QRCode(message_cause_problem, error_correction=qrcode.ERROR_CORRECTION.Q)
# qr = qrcode.QRCode(message_that_is_really_long, error_correction=qrcode.ERROR_CORRECTION.Q)

qr.generate()

# pprint(vars(qr))


tk = Tk()
ex = Example()
ex.draw(qr.module_matrix)
tk.mainloop()
