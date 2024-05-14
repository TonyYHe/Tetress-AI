from referee.game.constants import MAX_TURNS
from referee.game.constants import BOARD_N

WIN = 1
LOSS = -1
DRAW = 0

DELIM_LEN = 25

TURN_THRESHOLD = MAX_TURNS * 0.8 
TIME_OUT_FACTOR = 10

NUM_CELLS = BOARD_N * BOARD_N

# ============= game phase based on the number of empty cells ==================
MIDGAME_STAGE = NUM_CELLS * 0.7
LATEGAME_STAGE = NUM_CELLS * 0.5
ENDGAME_STAGE = NUM_CELLS * 0.3

# ============ game phase based on the number of legal actions =================
# MIDGAME_STAGE = 300
# LATEGAME_STAGE = 200
# ENDGAME_STAGE = 100

UPPER_BOUND = 'upperbound'
LOWER_BOUND = 'lowerbound'
EXACT = 'exact'

MAX_SEARCH_DEPTH = MAX_TURNS