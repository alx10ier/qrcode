import requests
import lxml
import bs4

res = requests.get('https://www.thonky.com/qr-code-tutorial/error-correction-table')
soup = bs4.BeautifulSoup(res.text, 'lxml')
table = soup.select('table.table.table-bordered')[0]
trs = table.find_all('tr')

# [[data_codewords], [ecc], [nb1], [nc1], [nb2], [nc2]]
L = [[],[],[],[],[],[]]
M = [[],[],[],[],[],[]]
Q = [[],[],[],[],[],[]]
H = [[],[],[],[],[],[]]

trs.pop(0)
trs.pop(19)
trs.pop(85)

for i in range(0, int(len(trs)/4)):
	for j in range(0, 6):
		L[j].append(int(trs[i*4].find_all('td')[j+1].get_text() or 0))
		M[j].append(int(trs[i*4+1].find_all('td')[j+1].get_text() or 0))
		Q[j].append(int(trs[i*4+2].find_all('td')[j+1].get_text() or 0))
		H[j].append(int(trs[i*4+3].find_all('td')[j+1].get_text() or 0))

output = open('codewords_table.py', 'w')

output.write('CODEWORDS = [\n')
output.write('\t' + str(L) +  ',\n')
output.write('\t' + str(M) +  ',\n')
output.write('\t' + str(Q) +  ',\n')
output.write('\t' + str(H) +  '\n')
output.write(']')
output.close()