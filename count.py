from collections import Counter
import sys
import matplotlib.pyplot as plt

# Run: python count.py src.txt dst.txt 
# Where src.txt and dst.txt are simple text files with a list of source and destination IP addresses


# frequency of sources
with open(sys.argv[1], "r") as f:
	# count frequency of each address
	freqSrc={}
	for line in f:
		l = line[:-1]
		if l in freqSrc:
			freqSrc[l] += 1
		else:
			freqSrc[l] = 1

	# create cumulative graph
	packetsSrc=[]
	sum = 0
	f.close()

	i=0
	print "Top 20 sources (by frequency)"
	for key, value in sorted(freqSrc.iteritems(), key=lambda (k,v): (v,k), reverse=True):
		if i < 20:
			print value, "\t", key
		i += 1
		packetsSrc.append(value + sum)
		sum = value + sum
	    # print key, value

# frequency of destinations
with open(sys.argv[2], "r") as f:
	# count frequency of each address
	freqDst={}
	for line in f:
		l = line[:-1]
		if l in freqDst:
			freqDst[l] += 1
		else:
			freqDst[l] = 1

	# create cumulative graph
	packetsDst=[]
	sum = 0
	f.close()
	
	i=0
	print
	print "Top 20 destinations (by frequency)"
	for key, value in sorted(freqDst.iteritems(), key=lambda (k,v): (v,k), reverse=True):
		packetsDst.append(value + sum)
		if i < 20:
			print value, "\t", key
		i += 1
		sum = value + sum
	    # print key, value


	plt.plot(packetsSrc, label='Source Addresses')
	plt.plot(packetsDst, label='Destination Addresses')
	plt.ylabel("cumulative packets")
	plt.xlabel("hitters")
	plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
	plt.show()

