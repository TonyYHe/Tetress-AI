# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

# This is the main entry point for the referee module. For detailed guidance on
# referee usage/command line options, run:
#
#   python -m referee --help
#
# NOTE: For the purposes of the project you do not need to understand all of
# the inner workings of this module. The only relevant parts are in the `game`
# module, as described in the project specification.

import os
import asyncio
from argparse import Namespace
from pathlib import Path
from traceback import format_tb

from .game import Player, PlayerColor
from .log import LogStream, LogColor, LogLevel
from .run import game_user_wait, run_game, \
    game_commentator, game_event_logger, game_delay, output_board_updates
from .agent import AgentProxyPlayer
from .options import get_options, PlayerLoc


def main(options: Namespace|None=None):
    if options is None:
        options = get_options()
    assert options is not None

    # Log config
    LogStream.set_global_setting("level", 
        [
            LogLevel.CRITICAL,
            LogLevel.INFO,
            LogLevel.INFO,
            LogLevel.DEBUG,
        ][options.verbosity])
    LogStream.set_global_setting("ansi", options.use_colour)
    LogStream.set_global_setting("unicode", options.use_unicode)

    # Referee log stream
    rl = LogStream("referee", LogColor.WHITE)
    rl.info("all messages printed by referee/wrapper modules begin with *")
    rl.info("(any other lines of output must be from your Agent class).")
    rl.info("\n")

    # Game log stream
    gl: LogStream | None = None
    gl_path: Path | None = None

    if options.logfile is not None:

        if options.logfile == 'stdout':
            # Standard stdout game log stream
            gl = LogStream(
                namespace="game",
                color=LogColor.YELLOW,
            )

        else:
            # File game log stream
            gl_path = Path(options.logfile)
            gl_path.parent.mkdir(parents=True, exist_ok=True)
            rl.debug(f"logging game output to '{gl_path}'")
            if gl_path.exists():
                rl.debug(f"clearing existing log file '{options.logfile}'")
                gl_path.unlink()

            def game_log_handler(message: str):
                if gl_path is not None:
                    with open(gl_path, "a") as f:
                        f.write(message + "\n")
            
            # File game log stream
            gl = LogStream(
                namespace="game", 
                ansi=False,
                handlers=[game_log_handler],
                output_namespace=False,
                output_level=False,
            )

    try:
        agents: dict[Player, dict] = {}
        for p_num, player_color in enumerate(PlayerColor, 1):
            # Import player classes
            player_loc: PlayerLoc = vars(options)[f"player{p_num}_loc"]
            player_name = f"player {p_num} [{':'.join(player_loc)}]"

            rl.info(f"wrapping {player_name} as {player_color}...")
            p: Player = AgentProxyPlayer(
                player_name,
                player_color,
                player_loc,
                time_limit=options.time,
                space_limit=options.space,
                log=LogStream(f"player{p_num}", LogColor[str(player_color)])
            )
            agents[p] = {
                "name": player_name,
                "loc": player_loc,
            }

        # Play the game!
        async def _run(options: Namespace) -> Player | None:
            event_handlers = [
                game_event_logger(gl) if gl is not None else None,
                game_commentator(rl),
                output_board_updates(rl, 
                                     options.use_colour, 
                                     options.use_unicode)\
                    if options.verbosity >= 2 else None,
                game_delay(options.wait) if options.wait > 0 else None,
                game_user_wait(rl) if options.wait < 0 else None,
            ]

            return await run_game(
                players=[p for p in agents.keys()],
                event_handlers=event_handlers,
            )
        
        result = asyncio.get_event_loop().run_until_complete(_run(options))

        # Print the final result under all circumstances
        if result is None:
            rl.critical("result: draw")
        else:
            rl.critical(f"result: {agents[result]['name']}")

        exit(0)

    except KeyboardInterrupt:
        rl.info()  # (end the line)
        rl.info("KeyboardInterrupt: bye!")

        rl.critical("result: <interrupt>")
        os.kill(os.getpid(), 9)

    except Exception as e:
        rl.critical(f"unhandled exception: {str(e)}")
        rl.critical("stack trace:")
        rl.critical(">> ")
        rl.critical(">> ".join(format_tb(e.__traceback__)))
        rl.critical("\n")
        rl.critical(
            f">> Please report this error to the course staff, including\n"
            f">> the trigger and the above stack trace.")

        rl.critical(f"result: <error>")
        exit(1)
