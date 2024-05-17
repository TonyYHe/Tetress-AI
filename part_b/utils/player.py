# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from enum import Enum

class PlayerColor(Enum):
    """
    An `enum` capturing the two player colours.
    """
    RED = 1
    BLUE = 2

    def __str__(self) -> str:
        """
        String representation of a player colour identifier.
        """
        return {
            PlayerColor.RED: "RED",
            PlayerColor.BLUE: "BLUE"
        }[self]

    def __index__(self) -> int:
        """
        Return the index of the player (0 or 1).
        """
        return self.value

    def __int__(self) -> int:
        """
        Player value in zero-sum form (+1 RED, -1 BLUE). 
        """
        return 1 - 2 * self.value

    @property
    def opponent(self) -> "PlayerColor":
        """
        Return the opposing player colour.
        """
        match self:
            case PlayerColor.RED:
                return PlayerColor.BLUE
            case PlayerColor.BLUE:
                return PlayerColor.RED
