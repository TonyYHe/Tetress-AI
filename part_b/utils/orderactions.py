from utils.node import *
from utils.table import *

class OrderActions:
    @staticmethod
    def order_actions(board: Board, actions: list, ttable: TranspositionTable, move_values):
        """
        Return a sorted list of actions based on best value stored in 
        transposition table, best value from previous iteration and heuristic 
        value.
        """
        move_scores = {}
        ordered_actions = []

        for action in actions:
            mutation = board.apply_action(action)
            ttentry: TTEntry = ttable.retrieve(board._state)
            if ttentry is not None:
                move_scores[board._state.__hash__()] = -ttentry.best_value
            else:
                if board._state in move_values:
                    move_scores[board._state.__hash__()] = -move_values[board._state.__hash__()]
                else:
                    move_scores[board._state.__hash__()] = OrderActions.heuristic_evaluate_action(action, board)
            board.undo_action(mutation)

        def get_move_score(action: PlaceAction):
            mutation = board.apply_action(action)
            value = move_scores[board._state.__hash__()]
            board.undo_action(mutation)
            return value

        ordered_actions = sorted(actions, key=get_move_score, reverse=True)
        return ordered_actions
    
    @staticmethod
    def topk_actions(actions):
        """
        Return the top k actions of the input list of action.
        """
        k = min(len(actions), 20)
        return actions[:k]
    
    @staticmethod
    def heuristic_evaluate_action(action: PlaceAction, board: Board):
        """
        Return the heuristic value of a node evaluated from the perspective of 
        the input player.
        """
        mutation = board.apply_action(action)
        if board._turn_count < 20:
            heuristic_value = board.diff_cells_occupied() + board.diff_reachable_valid_empty_cell()
        else:
            heuristic_value = board.diff_cells_occupied()*0.5 + board.diff_reachable_valid_empty_cell()
        board.undo_action(mutation)
        return -heuristic_value

        
