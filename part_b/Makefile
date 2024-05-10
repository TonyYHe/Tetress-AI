# Use "make run" to run "python3 -m referee agent (red) agent (blue)"
a1 = agentAB
a2 = agentRandom
smart_agents = $(a1) $(a1) 
dumb_agents = $(a2) $(a2) 
test_red = $(a1) $(a2) 
test_blue = $(a2) $(a1) 

smart: 
	python3 -m referee $(smart_agents)
dumb:
	python3 -m referee $(dumb_agents)
red:
	python3 -m referee $(test_red)
blue:
	python3 -m referee $(test_blue)

help: 
	python3 -m referee --$@

# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__