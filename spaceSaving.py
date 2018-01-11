import sys

SRC = './sourceCaida.txt'
K = 400

def getMinKey(table):
	minKey = ''
	minVal = sys.maxint

	for k in table:
		v = table[k]
		if v < minVal:
			minKey = k
			minVal = v
	return minKey



table = {}

with open(SRC) as f:  
	ip = f.readline().strip()
	while ip:

		if ip in table:
			table[ip] = table[ip] + 1
		else:
			if len(table) < K:
				table[ip] = 1
			else:
				minKey = getMinKey(table)
				minVal = table[minKey]
				table.pop(minKey)
				table[ip] = minVal + 1
		ip = f.readline().strip()

sorted_table = sorted(table, key=table.__getitem__, reverse=True)

for k in sorted_table:
	v = table[k]
	print k + '\t\t\t' + str(v)