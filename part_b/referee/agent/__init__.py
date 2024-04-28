# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from contextlib import contextmanager
from typing import Type

from ..game.player import Player
from ..log import LogStream, NullLogger
from ..game import Action, PlayerColor, PlayerException
from ..options import PlayerLoc, TIME_LIMIT_NOVALUE
from .client import RemoteProcessClassClient, AsyncProcessStatus, \
    WrappedProcessException
from .resources import ResourceLimitException

RECV_TIMEOUT = TIME_LIMIT_NOVALUE # Max seconds for agent to reply (wall clock)



class AgentProxyPlayer(Player):
    """
    Provide a wrapper for Agent classes to handle tedious details like resource
    utilisation checks and exception handling. Agents are run in a separate
    process so that they cannot interfere with the referee's game loop. Note
    that this class is implemented as an async context manager to implicitly
    take care of the agent's lifecycle.
    """

    def __init__(self, 
        name: str,
        color: PlayerColor, 
        agent_loc: PlayerLoc,
        time_limit: float | None, 
        space_limit: float | None, 
        res_limit_tolerance: float = 1.0,
        log: LogStream = NullLogger(),
        intercept_exc_type: Type[Exception] = PlayerException,
        subproc_output: bool = True,
    ):
        '''
        Create an agent proxy player.

        name: Name of the agent (for logging purposes).
        color: The player colour the agent is playing as. This is passed to the
            agent's constructor.
        agent_loc: Location of the agent package/class.
        time_limit: Maximum CPU time (in seconds) that the agent is allowed to
            run for in total. If None, no time limit is enforced.
        space_limit: Maximum memory (in MB) that the agent is allowed to use
            at any one time. If None, no space limit is enforced.
        res_limit_tolerance: A multiplier for resource limit enforcement, not
            known to the agent itself. For example, if the agent is allowed 1 
            second of CPU time, and the tolerance is 1.1, then the agent 
            will be allowed to run for 1.1 seconds before being terminated,
            but will only be told that it has used 1 second of CPU time.
        log: LogStream to use for logging.
        intercept_exc_type: Exception type to re-raised when an exception is
            caught from the agent process. 
        subproc_output: Whether to print the agent's stderr stream to the
            terminal. This is useful for debugging.
        '''
        super().__init__(color)

        assert isinstance(agent_loc, PlayerLoc), "agent_loc must be a PlayerLoc"
        self._pkg, self._cls = agent_loc
        
        self._name = name
        self._agent: RemoteProcessClassClient = RemoteProcessClassClient(
            self._pkg, self._cls, 
            time_limit = time_limit, 
            space_limit = space_limit, 
            res_limit_tolerance = res_limit_tolerance,
            recv_timeout = RECV_TIMEOUT, 
            subproc_output = subproc_output,
            log = log,
            # Class constructor arguments (passed to agent)
            color = color
        )
        self._log = log
        self._ret_symbol = f"⤷" if log.setting("unicode") else "->"
        self._InterceptExc = intercept_exc_type

    @contextmanager
    def _intercept_exc(self):
        try:
            yield

        # Reraising exceptions as PlayerExceptions to determine win/loss
        # outcomes in calling code (see the 'game' module).
        except ResourceLimitException as e:
            self._log.error(f"resource limit exceeded (pid={self._agent.pid}): {str(e)}")
            self._log.error("\n")
            self._log.error(self._summarise_status(self._agent.status))
            self._log.error("\n")

            raise self._InterceptExc(
                f"{str(e)} in {self._name} agent",
                self._color
            )

        except WrappedProcessException as e:
            err_lines = str(e.args[1]["stacktrace_str"]).splitlines()

            self._log.error(f"exception caught (pid={self._agent.pid}):")
            self._log.error("\n")
            self._log.error("\n".join([f">> {line}" for line in err_lines]))
            self._log.error("\n")

            raise self._InterceptExc(
                f"error in {self._name} agent\n"
                f"{self._ret_symbol} {err_lines[-1]}",
                self._color
            )
        
        except EOFError as e:
            self._log.error(f"EOFError caught (pid={self._agent.pid}):")

            raise self._InterceptExc(
                f"EOF reply from {self._name} (did the process exit?)",
                self._color
            )

    async def __aenter__(self) -> 'AgentProxyPlayer':
        # Import the agent class (in a separate process). Note: We are wrapping
        # another async context manager here, so need to use the __aenter__ and
        # __aexit__ methods.
        self._log.debug(f"creating agent subprocess...")
        with self._intercept_exc():
            await self._agent.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._agent.__aexit__(exc_type, exc_value, traceback)
        self._log.debug(f"agent process terminated")

    async def action(self) -> Action:
        """
        Get the agent's action for the current turn.
        """
        self._log.debug(f"call 'action()'...")

        with self._intercept_exc():
            action: Action = await self._agent.action()

        self._log.debug(f"{self._ret_symbol} {action!r}")
        self._log.debug(self._summarise_status(self._agent.status))
        return action

    async def update(self, color: PlayerColor, action: Action):
        """
        Update the agent with the latest action from the game.
        """
        self._log.debug(f"call 'update({color!r}, {action!r})'...")

        with self._intercept_exc():
            await self._agent.update(color, action)

        self._log.debug(self._summarise_status(self._agent.status))

    def _summarise_status(self, status: AsyncProcessStatus | None):
        if status is None:
            return "resources usage status: unknown\n"

        time_str = f"  time:  +{status.time_delta:6.3f}s  (just elapsed)   "\
                   f"  {status.time_used:7.3f}s  (game total)\n"
        space_str = ""
        if status.space_known:
            space_str = f"  space: {status.space_curr:7.3f}MB (current usage)  "\
                        f"  {status.space_peak:7.3f}MB (peak usage)\n"
        else:
            space_str = "  space: unknown (check platform)\n"
        return f"resources usage status:\n{time_str}{space_str}"
