# Use "make run" to run "python3 -m referee agent (red) agent (blue)"
red = agent
blue = agentRandom

prefix = python3 -m referee -s 250 -t 180 $(red)
random:
	$(prefix) agentRandom
token: 
	$(prefix) greedy_token_agent	
actions: 
	$(prefix) greedy_legal_actions_agent
greedy: 
	$(prefix) greedy_agent

err: 
	python3 -m referee -s 250 -t 180 $(red) $(blue) 2> _out$(n).txt

# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__