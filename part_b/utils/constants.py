from referee.game.constants import MAX_TURNS
from referee.game.constants import BOARD_N
import numpy as np
DELIM_LEN = 25

TURN_THRESHOLD = MAX_TURNS * 0.8 
SAFE_RANDOM_TIME_OUT = 0.5

SAMPLE_SIZE = 30
BRANCHING_FACTOR = 3

# TETRESS CONSTANTS
NUM_CELLS = BOARD_N * BOARD_N

WIN = 1
LOSS = -1
DRAW = 0

# arrayboard representation
# EMPTY = 0
# RED = 1
# BLUE = -1
# EMPTY_BOARD = np.array([EMPTY for _ in range(NUM_CELLS)])

# bitboard representation
# EMPTY_BOARD = 0

# =============================== time allocation ==============================
MIDGAME_TIME = 4
LATEGAME_TIME = 5
TIME_OUT_FACTOR = 30
SAFE_RANDOM_TIME_OUT = 0.5

# ============================== space allocation ==============================
MAX_TABLE_SIZE = 300

# ============= game phase based on the number of empty cells ==================
# MIDGAME_STAGE = NUM_CELLS * 0.6
# LATEGAME_STAGE = NUM_CELLS * 0.4
# ENDGAME_STAGE = NUM_CELLS * 0.3

# ============ game phase based on the number of legal actions =================
MIDGAME_STAGE = 200
LATEGAME_STAGE = 20

UPPER_BOUND = 'upperbound'
LOWER_BOUND = 'lowerbound'
EXACT = 'exact'

MAX_SEARCH_DEPTH = MAX_TURNS