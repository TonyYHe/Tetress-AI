# Use "make run" to run "python3 -m referee agent (red) agent (blue)"
red = agentAB
blue = agentRandom

run:
	python3 -m referee -s 250 -t 180 $(red) $(blue)

err: 
	python3 -m referee -s 250 -t 180 agentAB agentRandom 2> _out$(n).txt

# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__