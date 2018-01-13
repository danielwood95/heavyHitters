echo "eviction rate = 1"
python hashPipe.py 1 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt
echo "eviction rate = 0.5"
python hashPipe.py 0.5 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt
echo "eviction rate = 0.3"
python hashPipe.py 0.3 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt
echo "eviction rate = 0.1"
python hashPipe.py 0.1 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt
echo "eviction rate = 0.07"
python hashPipe.py 0.07 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt
echo "eviction rate = 0.05"
python hashPipe.py 0.05 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt
echo "eviction rate = 0.04"
python hashPipe.py 0.04 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt
echo "eviction rate = 0.02"
python hashPipe.py 0.02 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt
echo "eviction rate = 0.01"
python hashPipe.py 0.01 > resultsHash5.txt
python countFalseNegatives.py resultsHash5.txt