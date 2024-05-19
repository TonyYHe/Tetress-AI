from utils.node import *
from utils.table import *

class OrderActions:
    @staticmethod
    def order_actions(board: Board, actions: list, player_color: PlayerColor, ttable: TranspositionTable):
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
                move_scores[board._state.__hash__()] = ttentry.best_value
            else:
                move_scores[board._state.__hash__()] = OrderActions.heuristic_evaluate_action(action, board, player_color)
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
    def heuristic_evaluate_action(action: PlaceAction, board: Board, player_color: PlayerColor):
        """
        Return the heuristic value of a node evaluated from the perspective of 
        the input player.
        """
        mutation = board.apply_action(action)
        heuristic_value = board.diff_cells_occupied() + board.diff_legal_actions()
        board.undo_action(mutation)
        if player_color == board._turn_color:
            return heuristic_value
        return -heuristic_value

        
