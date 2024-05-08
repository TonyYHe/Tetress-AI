# Use "make run" to run "python3 -m referee agent (red) agent (blue)"
a1 = agent 
a2 = agent
a3 = random_agent
a4 = random_agent
a5 = habp_agent
a6 = habp_agent
mcts_mcts = $(a1) $(a2) 
random_random = $(a3) $(a4) 
habp_habp = $(a5) $(a6) 
random_mcts_red = $(a1) $(a3) 
random_mcts_blue = $(a3) $(a1) 
random_habp_red = $(a5) $(a3) 
random_habp_blue = $(a3) $(a5) 


run_mcts_mct: 
	python3 -m referee $(mcts_mcts)
run_random_random:
	python3 -m referee $(random_random)
run_habp_habp:
	python3 -m referee $(habp_habp)
run_random_mcts_red:
	python3 -m referee $(random_mcts_red)
run_random_mcts_blue:
	python3 -m referee $(random_mcts_blue)
run_random_habp_red:
	python3 -m referee $(random_habp_red)
run_random_habp_blue:
	python3 -m referee $(random_habp_blue)


# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__