# Use "make run" to run "python3 -m referee agent (red) agent (blue)"
a1 = agentAB
a2 = agentRandom
smart_agents = $(a1) $(a1) 
dumb_agents = $(a2) $(a2) 
test_agents_red = $(a1) $(a2) 
test_agents_blue = $(a2) $(a1) 

run_smart: 
	python3 -m referee $(smart_agents)
run_dumb:
	python3 -m referee $(dumb_agents)
run_test_red:
	python3 -m referee $(test_agents_red)
run_test_blue:
	python3 -m referee $(test_agents_blue)

# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__