import sys
import random
import math
from sets import Set
import matplotlib.pyplot as plt

DATA_FILES = [ 'srcCaida500000.txt', 'srcCaida2.txt',]
HASH_PIPE_PARAMS = {'MEM_SIZE': 4500, 'D': 6, 'RAND_TRIALS': 2}
TOP_K =  300

def countFalseNegatives(reference, test_results):
	
	ref = reference[:TOP_K]
	count = 0


	for x in ref:
		if x == []:
			continue
		if x not in test_results:
			count += 1

	return count

def wrapFormula(val):
	return (1 / (5 * math.log(val+1) ))

def getHash(s, stage, size):
	return abs(hash(s + str(stage))) % size

def getHashRandom(size):
	return random.randint(0,size-1)

def hashPipe(dataList, params, allRand=False, feedback=False, firstRand=False, lastRand=False, saveFirstRand=False, frontReject=False):
	MEM_SIZE = params['MEM_SIZE']
	D = params['D']
	STAGE_SIZE = int(MEM_SIZE / D)

	table = [[(0,0) for i in range(STAGE_SIZE)] for j in range(D)]

	for ip in dataList:

		if allRand or firstRand:
			index = getHashRandom(STAGE_SIZE)
		else:
			index = getHash(ip, 0, STAGE_SIZE)
		key = table[0][index][0]
		val = table[0][index][1]	

		if key == ip:
			table[0][index] = (key, val + 1)
		elif val == 0:
			table[0][index] = (ip, 1)
		else:

			if frontReject:
				r = random.uniform(0,1)
				if r > wrapFormula(val):
					continue

			orig_index = index
			cKey = ip
			cVal = val

			for i in range(1,D):
				
				if allRand or lastRand:
					index = getHashRandom(STAGE_SIZE)
				else:
					index = getHash(ip, i, STAGE_SIZE)
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

			if feedback:
				r = random.uniform(0,1)
				if r > wrapFormula(cVal):
					if saveFirstRand:
						index = orig_index
					elif allRand:
						index = getHashRandom(STAGE_SIZE)
					else:
						index = getHash(ip,0,STAGE_SIZE)
					table[0][index] = (cKey,cVal)

	s = Set()
	for stg in table:
		for x in stg:
			if x[0] != 0:
				s.add(x[0])

	return s

###################################################################

N = len(DATA_FILES)
data = [[] for i in range(N)]
sorted_data = [[] for i in range(N)]
verbose = False

try:
	if "-v" in sys.argv:
		verbose = True
	if "-p" in sys.argv:
		plot = True
except IndexError:
	pass

if plot:
	pRange = range(300, 3001, 600)
	#pRange = range(6,11)
else:
	pRange = range(0,1)

lists = [[pRange, []] for i in range(10)]

# Read and sort all data
for i in range(N):
	freqSrc={}
	with open("./" + DATA_FILES[i]) as f:
		for line in f:
			l = line.strip()

			data[i].append(l)
			if l in freqSrc:
				freqSrc[l] += 1
			else:
				freqSrc[l] = 1

		for key, value in sorted(freqSrc.iteritems(), key=lambda (k,v): (v,k), reverse=True):
			sorted_data[i].append(key)

for h in pRange:
	#HASH_PIPE_PARAMS['D'] = h
	HASH_PIPE_PARAMS['MEM_SIZE'] = h


	print str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."


	# 0: hashPipe

	if verbose:
		print "Testing hashPipe with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters and " + str(HASH_PIPE_PARAMS['D']) + " stages..."
		print "------------------------------------------------------------"

	total = 0
	for i in range(N):

		results = hashPipe(data[i], HASH_PIPE_PARAMS)
		negs = countFalseNegatives(sorted_data[i], results)
		rate = negs / float(TOP_K)
		total += negs

		if verbose:
			print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " false negative rate (" + str(negs) + "/" + str(TOP_K) + ")"

	tot_rate = total / float(TOP_K * N)
	print "Standard aggregate rate: " + str(tot_rate)
	lists[0][1].append(tot_rate)


	# 1: hashPipeInterview


	if verbose:
		print "Testing hashPipeInterview with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters and " + str(HASH_PIPE_PARAMS['D']) + " stages..."
		print "------------------------------------------------------------"

	total = 0
	for i in range(N):

		results = hashPipe(data[i], HASH_PIPE_PARAMS, feedback=True)
		negs = countFalseNegatives(sorted_data[i], results)
		rate = negs / float(TOP_K)
		total += negs

		if verbose:
			print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " false negative rate (" + str(negs) + "/" + str(TOP_K) + ")"
	tot_rate = total / float(TOP_K * N)
	print "Interview aggregate rate: " + str(tot_rate)
	lists[1][1].append(tot_rate)


	# 2: hashPipeRandom

	# if verbose:
	# 	print "Testing hashPipeRandom with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	# 	print "------------------------------------------------------------"

	# total = 0
	# for i in range(N):

	# 	trial_negs = 0
	# 	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
	# 		results = hashPipe(data[i], HASH_PIPE_PARAMS, allRand=True)
	# 		trial_negs += countFalseNegatives(sorted_data[i], results)

	# 	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# 	total += trial_negs
	# 	if verbose:
	# 		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

	# tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# print "Randomize all aggregate rate: " + str(tot_rate)
	# lists[2][1].append(tot_rate)



	# 3: hashPipeBouncer


	# if verbose:
	# 	print "Testing hashPipeBouncer with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	# 	print "------------------------------------------------------------"

	# total = 0
	# for i in range(N):

	# 	trial_negs = 0
	# 	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
	# 		results = hashPipe(data[i], HASH_PIPE_PARAMS, frontReject=True)
	# 		trial_negs += countFalseNegatives(sorted_data[i], results)

	# 	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# 	total += trial_negs
	# 	if verbose:
	# 		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

	# tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# print "Bouncer aggregate rate: " + str(tot_rate)
	# lists[3][1].append(tot_rate)



	# 4: hashPipeRandomInterview


	if verbose:
		print "Testing hashPipeRandomInterview with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
		print "------------------------------------------------------------"

	total = 0
	for i in range(N):

		trial_negs = 0
		for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
			results = hashPipe(data[i], HASH_PIPE_PARAMS, allRand=True, feedback=True)
			trial_negs += countFalseNegatives(sorted_data[i], results)

		rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
		total += trial_negs
		if verbose:
			print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

	tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
	print "Randomize all and interview aggregate rate: " + str(tot_rate)
	lists[4][1].append(tot_rate)


	# 5: hashPipefRand

	# if verbose:
	# 	print "Testing hashPipefRand with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	# 	print "------------------------------------------------------------"

	# total = 0
	# for i in range(N):

	# 	trial_negs = 0
	# 	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
	# 		results = hashPipe(data[i], HASH_PIPE_PARAMS, firstRand=True)
	# 		trial_negs += countFalseNegatives(sorted_data[i], results)

	# 	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# 	total += trial_negs
	# 	if verbose:
	# 		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

	# tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# print "Randomize first stage (hash others) aggregate rate: " + str(tot_rate)
	# lists[5][1].append(tot_rate)



	# 6: hashPipefRandSave

	# if verbose:
	# 	print "Testing hashPipefRandSave with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	# 	print "------------------------------------------------------------"

	# total = 0
	# for i in range(N):

	# 	trial_negs = 0
	# 	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
	# 		results = hashPipe(data[i], HASH_PIPE_PARAMS, firstRand=True, feedback=True, saveFirstRand=True)
	# 		trial_negs += countFalseNegatives(sorted_data[i], results)

	# 	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# 	total += trial_negs
	# 	if verbose:
	# 		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

	# tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# print "Randomize first stage, save index for interview aggregate rate: " + str(tot_rate)
	# lists[6][1].append(tot_rate)



	# 7: hashPipefRandInterview

	if verbose:
		print "Testing hashPipefRandInterview with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
		print "------------------------------------------------------------"

	total = 0
	for i in range(N):

		trial_negs = 0
		for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
			results = hashPipe(data[i], HASH_PIPE_PARAMS, firstRand=True, feedback=True)
			trial_negs += countFalseNegatives(sorted_data[i], results)

		rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
		total += trial_negs
		if verbose:
			print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

	tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
	print "Randomize first stage and interview aggregate rate: " + str(tot_rate)
	lists[7][1].append(tot_rate)

	# 8: hashPipelRand

	# if verbose:
	# 	print "Testing hashPipelRand with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	# 	print "------------------------------------------------------------"

	# total = 0
	# for i in range(N):

	# 	trial_negs = 0
	# 	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
	# 		results = hashPipe(data[i], HASH_PIPE_PARAMS, lastRand=True)
	# 		trial_negs += countFalseNegatives(sorted_data[i], results)

	# 	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# 	total += trial_negs
	# 	if verbose:
	# 		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

	# tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# print "Randomize all except first stage aggregate rate: " + str(tot_rate)
	# lists[8][1].append(tot_rate)


	# 9: hashPipefRandBouncer

	# if verbose:
	# 	print "Testing hashPipefRandBouncer with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	# 	print "------------------------------------------------------------"

	# total = 0
	# for i in range(N):

	# 	trial_negs = 0
	# 	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
	# 		results = hashPipe(data[i], HASH_PIPE_PARAMS, firstRand=True, frontReject=True)
	# 		trial_negs += countFalseNegatives(sorted_data[i], results)

	# 	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# 	total += trial_negs
	# 	if verbose:
	# 		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

	# tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
	# print "Randomize first stage, bouncer aggregate rate: " + str(tot_rate)
	# lists[9][1].append(tot_rate)

if plot:
	p0 = plt.plot(lists[0][0], lists[0][1], label='hashPipe', marker='o')
	p1 = plt.plot(lists[1][0], lists[1][1], label='hashPipeInterview', marker='o')
	# p2 = plt.plot(lists[2][0], lists[2][1], label='hashPipeRandom', marker='o')
	# p3 = plt.plot(lists[3][0], lists[3][1], label='hashPipeBouncer', marker='o')
	p4 = plt.plot(lists[4][0], lists[4][1], label='hashPipeRandomInterview', marker='o')
	# p5 = plt.plot(lists[5][0], lists[5][1], label='hashPipefRand', marker='o')
	# p6 = plt.plot(lists[6][0], lists[6][1], label='hashPipefRandSave', marker='o')
	p7 = plt.plot(lists[7][0], lists[7][1], label='hashPipefRandInterview', marker='o')
	# p8 = plt.plot(lists[8][0], lists[8][1], label='hashPipelRand', marker='o')
	# p9 = plt.plot(lists[9][0], lists[9][1], label='hashPipefRandBouncer', marker='o')
	plt.ylabel("False negative rate")
	plt.xlabel("Number of counters")
	plt.legend()
	plt.title('False Negative Rate vs. # of table stages, k=300, D=6')
	plt.show()

