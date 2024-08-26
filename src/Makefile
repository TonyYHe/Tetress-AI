# Use "make run RED=a1 BLUE=a2", where a1_agent is an agent folder. Similarly 
# with a2.
run:
	python3 -m referee -s 250 -t 180 $(RED)_agent $(BLUE)_agent
.PHONY: run

# Use "make clean" to clean all the cache files in current and the next 3 layers of subdirectories 
clean: 
	rm -r __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__