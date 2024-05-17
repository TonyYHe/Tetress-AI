from disposed.boardstate import *

board = BoardState()

print(board.get_cell(0,0))
board.set_cell(1,2,1)
print(board.get_cell(1,2))
print(board.display())
