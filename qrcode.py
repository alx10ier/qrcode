# todo: @feature support model 1
# todo: @feature support frame qr
# todo: @dev put steps into seperate functions

import data
import error_correction
import module

from data import ERROR_CORRECTION

class QRCode:

	def __init__(self, data, error_correction=ERROR_CORRECTION.M):
		'''
		support string data only for now,
		todo: @feature should support more types in the furture.
		'''
		self.data = data
		self.error_correction = error_correction

	def generate(self):
		self.mode = data.determine_mode(self.data)
		self.version = data.determine_version(self.data, self.error_correction, self.mode)
		data_codewords = data.get_data_codewords(self.data, self.error_correction, self.mode, self.version)
		error_correction_codewords = error_correction.get_error_correction_codewords(data_codewords, self.error_correction, self.version)
		final_message = data.get_final_message(data_codewords, error_correction_codewords, self.error_correction, self.version)
		self.module_matrix = module.get_module_matrix(final_message, self.version)