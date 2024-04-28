# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

class PlayerException(Exception):
    """Raised when a player does something illegal to result in
    a premature end to the game."""

class IllegalActionException(PlayerException):
    """Action is illegal based on the current board state."""
