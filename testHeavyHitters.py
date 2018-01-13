import sys
import random
import math
from sets import Set

DATA_FILES = [ 'srcCaida500000.txt', 'srcCaida2.txt',]
HASH_PIPE_PARAMS = {'MEM_SIZE': 4500, 'D': 6, 'RAND_TRIALS': 5}
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

def hashPipe(dataList, params, allRand=False, feedback=False, firstRand=False, lastRand=False, saveFirstRand=False):
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
	if sys.argv[1] == "-v":
		verbose = True
except IndexError:
	pass

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


# hashPipeFeedback


if verbose:
	print "Testing hashPipeFeedback with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters and " + str(HASH_PIPE_PARAMS['D']) + " stages..."
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
print "Feedback aggregate rate: " + str(tot_rate)


# hashPipeRandom

if verbose:
	print "Testing hashPipeRandom with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	print "------------------------------------------------------------"

total = 0
for i in range(N):

	trial_negs = 0
	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
		results = hashPipe(data[i], HASH_PIPE_PARAMS, allRand=True)
		trial_negs += countFalseNegatives(sorted_data[i], results)

	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	total += trial_negs
	if verbose:
		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
print "Randomize all aggregate rate: " + str(tot_rate)



# hashPipeRandomFeedback


if verbose:
	print "Testing hashPipeRandomFeedback with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
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
print "Randomize all and feedback aggregate rate: " + str(tot_rate)


#hashPipefRand
if verbose:
	print "Testing hashPipefRand with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	print "------------------------------------------------------------"

total = 0
for i in range(N):

	trial_negs = 0
	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
		results = hashPipe(data[i], HASH_PIPE_PARAMS, firstRand=True)
		trial_negs += countFalseNegatives(sorted_data[i], results)

	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	total += trial_negs
	if verbose:
		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
print "Randomize first stage (hash others) aggregate rate: " + str(tot_rate)



#hashPipefRandSave

if verbose:
	print "Testing hashPipefRandSave with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	print "------------------------------------------------------------"

total = 0
for i in range(N):

	trial_negs = 0
	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
		results = hashPipe(data[i], HASH_PIPE_PARAMS, firstRand=True, feedback=True, saveFirstRand=True)
		trial_negs += countFalseNegatives(sorted_data[i], results)

	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	total += trial_negs
	if verbose:
		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
print "Randomize first stage and save index for feedback aggregate rate: " + str(tot_rate)



#hashPipefRandFeedback

if verbose:
	print "Testing hashPipefRandFeedback with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
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
print "Randomize first stage and feedback aggregate rate: " + str(tot_rate)

#hashPipelRand

if verbose:
	print "Testing hashPipelRand with " + str(HASH_PIPE_PARAMS['MEM_SIZE']) + " counters, " + str(HASH_PIPE_PARAMS['D']) + " stages and " + str(HASH_PIPE_PARAMS['RAND_TRIALS']) + " random trials..."
	print "------------------------------------------------------------"

total = 0
for i in range(N):

	trial_negs = 0
	for j in range(HASH_PIPE_PARAMS['RAND_TRIALS']):
		results = hashPipe(data[i], HASH_PIPE_PARAMS, lastRand=True)
		trial_negs += countFalseNegatives(sorted_data[i], results)

	rate = trial_negs / float(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS'])
	total += trial_negs
	if verbose:
		print "Trial " + str(i+1) + " (" + str(len(data[i])) + " data points): " + str(rate) + " avg false negative rate (" + str(trial_negs) + "/" + str(TOP_K * HASH_PIPE_PARAMS['RAND_TRIALS']) + ")"

tot_rate = total / float(TOP_K * N * HASH_PIPE_PARAMS['RAND_TRIALS'])
print "Randomize all except first stage aggregate rate: " + str(tot_rate)

