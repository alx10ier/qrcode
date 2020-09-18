# -*- coding: UTF-8 -*-

from pprint import pprint
import qrcode 
import error_correction

qr = qrcode.QRCode('HELLO WORLD')

qr.generate()

pprint(vars(qr))