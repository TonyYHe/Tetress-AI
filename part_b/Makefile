# Use "make run" to run "python3 -m referee agent (red) agent (blue)"
a1 = random_agent
a2 = greedy_agent
a3 = mcts_agent
a4 = pvs_agent

random_random = $(a1) $(a1) 
greedy_greedy = $(a2) $(a2) 
random_greedy = $(a1) $(a2) 
greedy_random = $(a2) $(a1)

mcts_mcts = $(a3) $(a3) 
mcts_random = $(a3) $(a1) 
random_mcts = $(a1) $(a3)
mcts_greedy = $(a3) $(a2) 
greedy_mcts = $(a2) $(a3) 

pvs_pvs = $(a4) $(a4) 
pvs_random = $(a4) $(a1)
random_pvs = $(a1) $(a4) 
pvs_greedy = $(a4) $(a2) 
greedy_pvs = $(a2) $(a4) 

run_random_random:
	python3 -m referee -s 250 -t 180 $(random_random)
run_greedy_greedy:
	python3 -m referee -s 250 -t 180 $(greedy_greedy)
run_random_greedy:
	python3 -m referee -s 250 -t 180 $(random_greedy)
run_greedy_random:
	python3 -m referee -s 250 -t 180 $(greedy_random)

run_mcts_mct: 
	python3 -m referee -s 250 -t 180 $(mcts_mcts)
run_mcts_random:
	python3 -m referee -s 250 -t 180 $(mcts_random)
run_random_mcts:
	python3 -m referee -s 250 -t 180 $(random_mcts)
run_mcts_greedy:
	python3 -m referee -s 250 -t 180 $(mcts_greedy)
run_greedy_mcts:
	python3 -m referee -s 250 -t 180 $(greedy_mcts)

run_pvs_pvs:
	python3 -m referee -s 250 -t 180 $(pvs_pvs)
run_pvs_random:
	python3 -m referee -s 250 -t 180 $(pvs_random)
run_random_pvs:
	python3 -m referee -s 250 -t 180 $(random_pvs)
run_pvs_greedy:
	python3 -m referee -s 250 -t 180 $(pvs_greedy)
run_greedy_pvs:
	python3 -m referee -s 250 -t 180 $(greedy_pvs)

# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__