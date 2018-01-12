import math
import random
SRC = './srcCaida500000.txt'
MEM_SIZE = 300
D = 16
STAGE_SIZE = int(MEM_SIZE / D)

table = [[(0,0) for i in range(STAGE_SIZE)] for j in range(D)]

def getHash(s, stage):
	#return abs(hash(s + str(stage))) % STAGE_SIZE
	return random.randint(0,STAGE_SIZE-1)

with open(SRC) as f:  
	ip = f.readline().strip()

	while ip:
		index = getHash(ip, 0)
		key = table[0][index][0]
		val = table[0][index][1]	

		if key == ip:
			table[0][index] = (key, val + 1)
		elif val == 0:
			table[0][index] = (ip, 1)
		else:
			cKey = ip
			cVal = val

			for i in range(1,D):
				index = getHash(ip, i)
				key = table[i][index][0]
				val = table[i][index][1]

				if key == cKey:
					table[i][index] = (cKey, val + cVal)
					break
				elif val == 0:
					table[i][index] = (cKey, cVal)
					break
				elif val < cVal:
					tempKey = cKey
					tempVal = cVal
					cKey = key
					cVal = val
					table[i][index] = (tempKey, tempVal)

			r = random.uniform(0,1)
			if r > (1/(5*math.log(cVal+1))):
				index = getHash(ip,0)
				table[0][index] = (cKey,cVal)
		ip = f.readline().strip()

allTuples = []
for stg in table:
	for x in stg:
		if x[0] != 0:
			allTuples.append(x)

sortedTuples = sorted(allTuples, key=lambda tup: tup[1], reverse=True)

for t in sortedTuples:
	print str(t[0]) + '\t\t\t' + str(t[1])
