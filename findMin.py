import random
import matplotlib.pyplot as plt

T = 10000
K = 400

avgMins=[]
for x in xrange(1,100):
	sum = 0.
	for t in xrange(T):
		minimum = K
		for y in xrange(x):
			r = random.randint(1,K+1)
			minimum = min(r, minimum)
		sum += minimum
	avgMins.append(sum/T)

plt.plot(avgMins)
plt.show()


