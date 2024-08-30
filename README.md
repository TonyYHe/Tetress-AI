# Tetress-AI
An agent program to play the game of Tetress.

## Game Rules
See [here](doc/game_rules.pdf).

## Structure of Program
**src**: Here are all the codes
*****************************************************************************
All the gaming agents with their CORE algorithms only
- **random_agent**: Experimental AI that randomly selects legal actions.
- **greedy_agent**: Experimental AI that selects the action which results in 
highest expected utility based on the evaluation function.
- **greedy_legal_actions_agent**: Experimental AI that selects the move which 
results in the highest number of legal actions.
- **greedy_token_agent**: Experimental AI that selects the next move 
with highest number of associated tokens.
- **habp_agent**: AI using Heuristic Alpha Beta Pruning Search.
- **mcts_agent**: Experiental AI using Monte Carlo Tree Search. Currently broken.
- **mtdf_agent**: Experiental AI using Memory-enhanced Test Driver with node
    'n' and value 'f'. Still being optimised.
- **pvs_agent**: Experiental AI using Principal Variation Search.
*****************************************************************************
The Non-agent files
- **disposed**: Disposed files, though some may still see usage in the future
- **referee**: The referee program for running the game of Tetress
- **utils**: Other components of an AI implementation. Some are optimisation 
techniques applied to ALL gaming agents.

## Optimisation Techniques
### Heuristic Sorting
During expansion, the child nodes are sorted using an evaluation function, which is as follows:
```math
sorting\_utility(state) = \begin{cases}
diff\_row\_col\_occupied + diff\_reachable &,\text{if } turn_count \leq 20,\\
diff\_row\_col\_occupied * 0.5 + diff\_reachable  &, otherwise.
\end{cases}
```

### Top-K Pruning
Whenever nodes are expanded for searching, only the top 15 child nodes based on an evaluation function. This is because Tetress has a very high branching factor, especially in Early-game Stage and Mid-game stage. This renders even a complete depth-limited search unrealistic as it takes too much time, therefore it is more desirable to rely on a good approximation.

### Transposition Table
The transposition table caches previously seen positions and associated evaluations. 
```math
```

### Iterative Deepening & Time Allocation
Iterative deepening is used to allow better time management by enabling the algorithm to provide a best effort result (i.e. search as deep as possible within the allocated time).

## Execution
```
make run RED=random BLUE=habp
```
For more information see the [makefile](src/Makefile).








    



