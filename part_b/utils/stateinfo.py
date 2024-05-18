from utils.board import *
from utils.constants import *

class StateInformation:
    def __init__(self, board: Board):
        # compute legal actions of the player and the opponent
        self.curr_color = board._turn_color
        self.turn_count = board._turn_count
        self.player_legal_actions = board.get_legal_actions()
        self.num_player_legal_actions = len(self.player_legal_actions)
        board.modify_turn_color(self.curr_color.opponent)
        self.opponent_legal_actions = board.get_legal_actions()
        self.num_opponent_legal_actions = len(self.opponent_legal_actions)
        board.modify_turn_color(self.curr_color)

        # compute other statistics
        self.num_empty_cells = len(board._empty_coords())
        self.num_player_token_count = len(board._player_occupied_coords(self.curr_color))
        self.num_opponent_token_count = len(board._player_occupied_coords(self.curr_color.opponent))
        self.winner_color = board.winner_color
        self.num_empty_player_reachable = self.num_valid_reachable_cells(board, self.curr_color)
        self.num_empty_opponent_reachable = self.num_valid_reachable_cells(board, self.curr_color.opponent)

    
    def eval_fn(self, player_color: PlayerColor, ply: int):
        """
        problematic
        Return a utility value calculated from the persepctive of the input 
        player, given a board. The input player color should always be THE 
        PLAYER (YOU).
        """
        if self.winner_color is not None:
            if self.winner_color == player_color:
                return 1000 - ply
            else:
                return -1000 + ply
            
        # Find the difference in the number of actions 
        extra_num_actions = self.diff_legal_actions()
        extra_num_reachable = self.diff_reachable_valid_empty_cell()
        extra_num_occupied = self.diff_cells_occupied()

        if self.turn_count <= TURN_THRESHOLD:
            utility = extra_num_actions + extra_num_reachable + extra_num_occupied*0.1
        else:
            turns_exceed_threshold = self.turn_count - TURN_THRESHOLD
            utility = extra_num_actions + extra_num_reachable + extra_num_occupied*turns_exceed_threshold*0.5

        # since Tetress is a zero-sum game, we can take the negative of the 
        # utility value for the opponent
        return utility if player_color == self.curr_color else -utility
    
    
    def diff_cells_occupied(self) -> int:
        """
        Find the difference in the number of tokens between the player and the 
        opponent. 
        """
        return self.num_player_token_count - self.num_opponent_token_count

    def diff_legal_actions(self) -> int: 
        """
        Find the difference in the number of legal actions between the player and 
        the opponent. 
        """
        return self.num_player_legal_actions - self.num_opponent_legal_actions
    
    def diff_reachable_valid_empty_cell(self) -> int: 
        ''' Find the difference in the number of valid empty cells reachable 
            between the player and the opponent. 
            A cell is valid if it is connected to at least 3 other empty cells. 
        '''
        return self.num_empty_player_reachable - self.num_empty_opponent_reachable
    
    def empty_connected(self, board: Board, empty: Coord) -> set[Coord]:
        ''' Return the empty cells connected to the `empty` cell
        '''
        frontier = [empty]
        connected = {empty}
        while frontier: 
            visiting = frontier.pop()
            for adjacent in [visiting.__add__(direction) for direction in Direction]: 
                if board._cell_empty(adjacent) and adjacent not in connected: 
                    frontier.append(adjacent)
                    connected.add(adjacent)
        return connected
    
    def num_valid_reachable_cells(self, board:Board, player:PlayerColor) -> int: 
        reachable = 0
        visited = set()
        occupied = board._player_occupied_coords(player)
        for cell in occupied: 
            for adjacent in [cell.__add__(direction) for direction in Direction]: 
                if board._cell_empty(adjacent) and adjacent not in visited: 
                    connected = self.empty_connected(board, adjacent)
                    # _testing.show(connected, description="new empty region connected")
                    # _testing.show(visited, description="previously visited empty region")
                    assert(len(visited.intersection(connected)) == 0)  # `connected` should be a new region that has not been visited 
                    visited.update(connected)
                    
                    # Only add valid cell count to the output 
                    if len(connected) >= 4: 
                        reachable += len(connected)
        return reachable