import requests
import lxml
import bs4

res = requests.get('https://www.thonky.com/qr-code-tutorial/alignment-pattern-locations')
soup = bs4.BeautifulSoup(res.text, 'lxml') 
table = soup.select('table.table.table-bordered')[0]
trs = table.find_all('tr')

trs.pop(0)
trs.pop(27)

locations = []

for tr in trs:
	tds = tr.find_all('td')
	version_locations = []
	for i in range(1, 8):
		if tds[i].get_text():
			version_locations.append(int(tds[i].get_text()))
	locations.append(version_locations)

output = open('align_patterns_table.py', 'w')
output.write('ALIGN_PATTERN_LOCATIONS = ')
output.write(str(locations))
output.close()