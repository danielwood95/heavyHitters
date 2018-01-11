import sys
from sets import Set

REF_FILE = './sourceCaida.txt'
SIZE = 400


def sortRef(K):
	# count frequency of each address
	with open(REF_FILE, "r") as f:

		freqSrc={}
		for line in f:
			l = line[:-1]
			if l in freqSrc:
				freqSrc[l] += 1
			else:
				freqSrc[l] = 1

		sum = 0
		i=0
		ref_list = []
		for key, value in sorted(freqSrc.iteritems(), key=lambda (k,v): (v,k), reverse=True):
			ref_list.append(key)

		del ref_list[K:]
		return ref_list


test_results = sys.argv[1]
s = Set()

with open("./" + test_results, "r") as f:
	count = 0
	for line in f:
		count += 1
		key = line.split()[0].strip()
		s.add(key)
		if count >= SIZE:
			break

K = min(len(s), SIZE)

ref_list = sortRef(K)

count = 0

for x in ref_list:
	if x not in s:
		count += 1

print count
print count / float(SIZE)

