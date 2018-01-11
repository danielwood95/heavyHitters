SRC = './src.txt'
MEM_SIZE = 600
D = 6
STAGE_SIZE = MEM_SIZE / D

stage_init = [(0,0)] * STAGE_SIZE
table = [stage] * D

def getHash(s, stage):
	return abs(hash(s + str(stage))) % K

with open(SRC) as f:  
	ip = f.readline().strip()

	while ip:
		index = getHash(ip, 0)
		key = table[0][index][0]
		val = table[0][index][1]

		if key is ip:
			val += 1
		elif val is 0:
			table[0][index] = (ip, 1)
		else:
			cKey = key
			cVal = val

			for i in range(1,D):
				index = getHash(ip, i)
				key = table[i][index][0]
				val = table[i][index][1]

				if key is cKey:
					table[i][index][1] += cKey
					break
				elif val is 0:
					table[i][index] = (cKey, cVal)
					break
				elif val < cVal:
					tempKey = cKey
					tempVal = cVal
					cKey = key
					cVal = val
					table[i][index] = (tempKey, tempVal)

		ip = f.readline().strip()

all_Tuples = []
for stg in table:
	

sorted_by_second = sorted(data, key=lambda tup: tup[1])

for s in table:
	for x in s:
		if x[0] in hitter_dict:

		hitter_dict[x[0]] = x[1]



sorted_table = sorted(table, key=table.__getitem__, reverse=True)

for k in sorted_table:
	v = table[k]
	print k + '\t\t\t' + str(v)
