from utils.board import Board, Coord, CellState
from referee.log import LogStream, LogColor
from typing import Iterable

def prefix(n=37): 
    return "-"*n

def display(board:Board, description:str): 
    '''Display board for debug 
    '''
    stream = LogStream("debug", LogColor.WHITE)
    width = 40
    stream.info(f"\n{' game board '.center(width, '-')}")
    stream.info(f"\n{f" [ {description} ]".center(width, ' ')}")
    stream.info(
                    '\n'.join([f"{'':<10}{l}" for l in
                        board.render(
                            use_color=True,
                            use_unicode=True,
                        ).splitlines()
                    ])
                )
    stream.info(f"{''.center(width, '-')}\n\n")

def show(coords:Iterable[Coord], description:str="no description"): 
    '''Show a set of coordinates
    '''
    board = Board()
    for coord in coords: 
        board._state[coord] = CellState(player="@")
    
    display(board, description)
    