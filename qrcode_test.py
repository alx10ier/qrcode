# -*- coding: UTF-8 -*-

from pprint import pprint
import qrcode 

message_simple = 'HELLO WORLD'
message = 'This is the most important things that I have ever seen.'
message_cause_problem = 'This is the most important things that I have ever seen there days.'

#   qr = qrcode.QRCode(message, error_correction=qrcode.ERROR_CORRECTION.Q)
# qr = qrcode.QRCode(message_cause_problem, error_correction=qrcode.ERROR_CORRECTION.Q)

qr.generate()

pprint(vars(qr))