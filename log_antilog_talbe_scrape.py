import requests
import lxml
import bs4

res = requests.get('https://www.thonky.com/qr-code-tutorial/log-antilog-table')
soup = bs4.BeautifulSoup(res.text, 'lxml') 
table = soup.select('table.table.table-bordered')[0]
trs = table.find_all('tr')

integers = []

trs.pop(0)
trs.pop(78)

for tr in trs:
	tds = tr.find_all('td')
	integers.append(int(tds[1].get_text()))

output = open('log_antilog_table.py', 'w')
output.write('INTEGERS = ')
output.write(str(integers))
