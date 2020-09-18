import requests
import lxml
import bs4

res = requests.get('https://www.thonky.com/qr-code-tutorial/character-capacities')
soup = bs4.BeautifulSoup(res.text, 'lxml') 
table = soup.select('table.table.table-bordered')[0]
trs = table.find_all('tr')

NUMERIC = [[],[],[],[]]
ALPHANUMERIC = [[],[],[],[]]
BYTE = [[],[],[],[]]
KANJI = [[],[],[],[]]

def write_list(list):
	output.write('\t\t# L\n')
	output.write('\t\t' + str(list[0]) + ',\n')
	output.write('\t\t# M\n')
	output.write('\t\t' + str(list[1]) + ',\n')
	output.write('\t\t# Q\n')
	output.write('\t\t' + str(list[2]) + ',\n')
	output.write('\t\t# H\n')
	output.write('\t\t' + str(list[3]) + '\n')

trs.pop(0) # remove table head
trs.pop(19*4) # remove empty row


for i in range(0, int(len(trs)/4)):
	for j in range(0, 4):

		tds = trs[i*4+j].find_all('td')
		if len(tds) == 6:
			tds.pop(0)
		NUMERIC[j].append(int(tds[1].get_text()))
		ALPHANUMERIC[j].append(int(tds[2].get_text()))
		BYTE[j].append(int(tds[3].get_text()))
		KANJI[j].append(int(tds[4].get_text()))

output = open('capacities_table.py', 'w')

output.write('# CAPACITIES[DATA_MODE][ERROR_CORRECTION][version]\n')
output.write('CAPACITIES = [\n')

output.write('\t# NUMERIC\n')
output.write('\t[\n')
write_list(NUMERIC)
output.write('\t],\n')

output.write('\t# ALPHANUMERIC\n')
output.write('\t[\n')
write_list(ALPHANUMERIC)
output.write('\t],\n')

output.write('\t# BYTE\n')
output.write('\t[\n')
write_list(BYTE)
output.write('\t],\n')

output.write('\t# KANJI\n')
output.write('\t[\n')
write_list(KANJI)
output.write('\t]\n')

output.write(']\n')
output.close()