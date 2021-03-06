from util import exponent_to_int, int_to_exponent
from codewords_table import CODEWORDS

def get_error_correction_codewords(dc, ec, version):
	blocks = []

	for dc_block in dc:
		ecc_len = CODEWORDS[ec.value][1][version-1]

		generator_polynomial = get_generator_polynomial(ecc_len)
		message_polynomial = get_message_polynomial(dc_block)

		generator_polynomial = generator_polynomial.multiply(Term(1, len(dc_block)-1))
		message_polynomial = message_polynomial.multiply(Term(1, ecc_len))

		blocks.append(divide_polynomials(message_polynomial, generator_polynomial))

	return blocks

def get_generator_polynomial(num):
	current = Polynomial(ComplexCoefficent(0), ComplexCoefficent(0))
	other = Polynomial(ComplexCoefficent(0), ComplexCoefficent(1))
	current = current.multiply(other)
	for i in range(2, num):
		next = Polynomial(ComplexCoefficent(0), ComplexCoefficent(i))
		current = current.multiply(next)
	return current

def get_message_polynomial(dc):
	result = Polynomial(*dc)
	return result

def divide_polynomials(message_polynomial, generator_polynomial):
	# todo: not sure if this part is alright
	if message_polynomial.terms[0].coefficient == 0:
		message_polynomial.terms.pop(0)
		generator_polynomial = generator_polynomial.multiply(Term(0, -1))

	exponent = int_to_exponent(message_polynomial.terms[0].coefficient)
	generator_polynomial_int = \
		generator_polynomial.multiply(Term(ComplexCoefficent(exponent), 0)).get_int_form()
	generator_polynomial = generator_polynomial.multiply(Term(0, -1))
	message_polynomial = message_polynomial.XOR(generator_polynomial_int)

	if message_polynomial.terms[-1].exponent == 0:
		return message_polynomial.get_coefficients()
	else:
		return divide_polynomials(message_polynomial, generator_polynomial)

class Polynomial:

	def __init__(self, *coefficients):
		if len(coefficients):
			if isinstance(coefficients[0], Term):
				self.terms = list(coefficients)
			else:
				self.terms = [Term(coefficients[i],
					len(coefficients)-i-1) for i in range(0, len(coefficients))]

	def __repr__(self):
		return str(self.terms)

	def __len__(self):
		return len(self.terms)

	def get_coefficients(self):
		return [term.coefficient for term in self.terms]

	def multiply(self, other):
		new_terms = []

		if isinstance(other, Polynomial):
			for term1 in self.terms:
				for term2 in other.terms:
					new_terms.append(term1.multiply(term2))

		if isinstance(other, Term):
			new_terms = [term.multiply(Term(other.coefficient, other.exponent)) for term in self.terms]


		new_polynomial = Polynomial(*new_terms)
		if isinstance(new_terms[0].coefficient, ComplexCoefficent):
			new_polynomial.mergeComplex()
		return new_polynomial

	def XOR(self, other):
		new_terms = []
		length = min(len(self), len(other))
		i = 1 # the coefficent of leading term of the result will always be 0, so just ignore it
		while i < length:
			term = self.terms[i].XOR(other.terms[i])
			new_terms.append(term)
			i += 1

		longer_terms = self.terms if len(self) > len(other) else other.terms
		for j in range(i, len(longer_terms)):
			new_terms.append(longer_terms[j])
		return Polynomial(*new_terms)

	def mergeComplex(self):
		new_terms = []
		indexes_to_remove = []
		for i in range(0, len(self)-1):
			for j in range(i+1, len(self)):
				if self.terms[i].exponent == self.terms[j].exponent:
					sum = exponent_to_int(self.terms[i].coefficient.exponent) ^ \
						exponent_to_int(self.terms[j].coefficient.exponent)
					coefficient = ComplexCoefficent(int_to_exponent(sum))
					exponent = self.terms[i].exponent
					term = Term(coefficient, exponent)
					new_terms.append(term)
					indexes_to_remove.append(i)
					indexes_to_remove.append(j)
		for index in sorted(indexes_to_remove, reverse=True):
			self.terms.pop(index)
		for term in new_terms:
			self.terms.append(term)
		self.terms.sort(key=lambda x: x.exponent, reverse=True)

	def get_int_form(self):
		new_terms = [term.get_int_form() for term in self.terms]
		return Polynomial(*new_terms)

	def get_exponent_form(self):
		new_terms = [term.get_exponent_form() for term in self.terms]
		return Polynomial(*new_terms)

class Term:
	def __init__(self, coefficient, exponent):
		self.coefficient = coefficient
		self.exponent = exponent

	def __repr__(self):
		return '{}x{}'.format(self.coefficient, self.exponent)

	def multiply(self, other):
		if isinstance(self.coefficient, ComplexCoefficent):
			if isinstance(other.coefficient, ComplexCoefficent):
				sum = self.coefficient.exponent + other.coefficient.exponent
				if sum > 255:
					sum %= 255
				coefficient = ComplexCoefficent(sum)
				
			else:
				# do NOT support multiply between normal coefficient and ComplexCoeffiecnt
				coefficient = self.coefficient
		else:
			coefficient = self.coefficient * other.coefficient
		exponent = self.exponent + other.exponent
		return Term(coefficient, exponent)

	def XOR(self, other):
		coefficient = self.coefficient ^ other.coefficient
		return Term(coefficient, self.exponent)

	def get_int_form(self):
		return Term(exponent_to_int(self.coefficient.exponent), self.exponent)

	def get_exponent_form(self):
		return Term(ComplexCoefficent(int_to_exponent(self.coefficient)), self.exponent)

class ComplexCoefficent:
	def __init__(self, exponent):
		self.exponent = exponent

	def __repr__(self):
		return 'a{}'.format(self.exponent)
	