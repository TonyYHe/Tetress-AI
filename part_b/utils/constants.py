from referee.game.constants import MAX_TURNS
from referee.game.constants import BOARD_N

WIN = 1
LOSS = -1
DRAW = 0

TURN_THRESHOLD = MAX_TURNS * 0.8 

NUM_CELLS = BOARD_N * BOARD_N

# ================= based on the number of legal actions =====================
# MIDGAME_STAGE = 300
# LATEGAME_STAGE = 200
# ENDGAME_STAGE = 100

# ================= based on the number of empty cells =====================
MIDGAME_STAGE = NUM_CELLS * 0.5
LATEGAME_STAGE = NUM_CELLS * 0.3
ENDGAME_STAGE = NUM_CELLS * 0.1
