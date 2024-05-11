# Use "make run" to run "python3 -m referee agent (red) agent (blue)"
a1 = random_agent
a2 = greedy_agent
a3 = mcts_agent
a4 = habp_agent

random_random = $(a1) $(a1) 
greedy_greedy = $(a2) $(a2) 
random_greedy = $(a1) $(a2) 
greedy_random = $(a2) $(a1)

mcts_mcts = $(a3) $(a3) 
mcts_random = $(a3) $(a1) 
random_mcts = $(a1) $(a3)
mcts_greedy = $(a3) $(a2) 
greedy_mcts = $(a2) $(a3) 

habp_habp = $(a4) $(a4) 
habp_random = $(a4) $(a1)
random_habp = $(a1) $(a4) 
habp_greedy = $(a4) $(a2) 
greedy_habp = $(a2) $(a4) 

run_random_random:
	python3 -m referee $(random_random)
run_greedy_greedy:
	python3 -m referee $(greedy_greedy)
run_random_greedy:
	python3 -m referee $(random_greedy)
run_greedy_random:
	python3 -m referee $(greedy_random)

run_mcts_mct: 
	python3 -m referee $(mcts_mcts)
run_mcts_random:
	python3 -m referee $(mcts_random)
run_random_mcts:
	python3 -m referee $(random_mcts)
run_mcts_greedy:
	python3 -m referee $(mcts_greedy)
run_greedy_mcts:
	python3 -m referee $(greedy_mcts)

run_habp_habp:
	python3 -m referee $(habp_habp)
run_habp_random:
	python3 -m referee $(habp_random)
run_random_habp:
	python3 -m referee $(random_habp)
run_habp_greedy:
	python3 -m referee $(habp_greedy)
run_greedy_habp:
	python3 -m referee $(greedy_habp)

# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__