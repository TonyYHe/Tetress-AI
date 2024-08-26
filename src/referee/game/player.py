# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from enum import Enum
from abc import ABC, abstractmethod
from .actions import Action


class PlayerColor(Enum):
    """
    An `enum` capturing the two player colours.
    """
    RED = 0
    BLUE = 1

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



class Player(ABC):
    """
    An abstract base class for a player in the game, used internally by the
    referee as an interface to an agent or human player.
    """
    def __init__(self, color: PlayerColor):
        self._color = color

    @property
    def color(self) -> PlayerColor:
        return self._color

    def __str__(self) -> str:
        return str(self._color)

    @abstractmethod
    async def action(self) -> Action:
        """
        Get the next action for the player.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, color: PlayerColor, action: Action):
        """
        Notify the player that an action has been played.
        """
        raise NotImplementedError

    async def __aenter__(self) -> 'Player':
        """
        Context manager: Any resource allocation should be done here.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager: Any resource cleanup should be done here.
        """
        pass
