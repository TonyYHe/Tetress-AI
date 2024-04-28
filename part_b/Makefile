# Use "make run" to run "python -m referee agent agent"
a1 = agent 
a2 = agent
agents = $(a1) $(a2) 
run: 
	python -m referee $(agents)

# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__