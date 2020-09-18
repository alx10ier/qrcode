from log_antilog_table import INTEGERS

def get_generator_polynomial(num):
	current = Polynomial(ComplexCoefficent(0), ComplexCoefficent(0))
	other = Polynomial(ComplexCoefficent(0), ComplexCoefficent(1))
	current = current.multiply(other)
	for i in range(2, num):
		next = Polynomial(ComplexCoefficent(0), ComplexCoefficent(i))
		current = current.multiply(next)
	return current

def get_message_polynomial(coefficients):
	result = Polynomial(*coefficients)
	return result

def exponent_to_int(num):
		if num > 255:
			num %= 255
		return INTEGERS[num]

def int_to_exponent(num):
		return INTEGERS.index(num)

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

	def multiply(self, other):
		new_terms = []
		for term1 in self.terms:
			for term2 in other.terms:
				new_terms.append(term1.multiply(term2))

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

	def multiplyByExponent(self, exponent):
		new_terms = [term.multiply(Term(1, exponent)) for term in self.terms]
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
		return Term(ComplexCoefficent(self.coefficient), self.exponent)

class ComplexCoefficent:
	def __init__(self, exponent):
		self.exponent = exponent

	def __repr__(self):
		return 'a{}'.format(self.exponent)
	