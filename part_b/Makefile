# Use "make run" to run "python3 -m referee agent (red) agent (blue)"
a1 = agent 
a2 = agent
a3 = random_agent
a4 = random_agent
smart_agents = $(a1) $(a2) 
dumb_agents = $(a3) $(a4) 
test_agents_red = $(a1) $(a3) 
test_agents_blue = $(a3) $(a1) 

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