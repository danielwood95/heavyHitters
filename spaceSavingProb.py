import sys
import random
import math

SRC = './srcCaida500000.txt'
K = 900

def getProbMinKey(table):
	minKey = ''
	minVal = sys.maxint

	for i in range(0, 10):

		r = random.choice(table.keys())
		v = table[r]
		if v < minVal:
			minKey = r
			minVal = v
	return minKey


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
				# probability of eviction
				r = random.uniform(0,1)
				minKey = getProbMinKey(table)
				minVal = table[minKey]
				if r < (1/(5*math.log(minVal+1))):
				#if r < 1/(minVal + 1):
				#if r < 0.02:
					table.pop(minKey)
					table[ip] = minVal + 1
		ip = f.readline().strip()

sorted_table = sorted(table, key=table.__getitem__, reverse=True)

for k in sorted_table:
	v = table[k]
	print k + '\t\t\t' + str(v)