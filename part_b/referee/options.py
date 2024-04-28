# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from dataclasses import dataclass
import sys
import argparse
from .game import PlayerColor, GAME_NAME, NUM_PLAYERS


# Program information:
PROGRAM = "referee"
VERSION = "2024.0.0"
DESCRIP = (
    f"Conduct a game of {GAME_NAME} between {NUM_PLAYERS} Agent classes."
)
F_WIDTH = 79

WELCOME = \
f"""{'':*^{F_WIDTH}}
Welcome to {GAME_NAME} referee version {VERSION}.

{DESCRIP}

Run `python -m referee --help` for additional usage information.
{'':*^{F_WIDTH}}"""

# default values (to use if flag is not provided)
# and missing values (to use if flag is provided, but with no value)

WAIT_DEFAULT = 0  # signifying no delay
WAIT_NOVALUE = 0.5  # seconds (between turns)

SPACE_LIMIT_DEFAULT = 0  # signifying no limit
SPACE_LIMIT_NOVALUE = 250.0  # MB (each player)
TIME_LIMIT_DEFAULT = 0  # signifying no limit
TIME_LIMIT_NOVALUE = 180.0  # seconds (each)

VERBOSITY_LEVELS = 4
VERBOSITY_DEFAULT = 2  # normal level, logs + board
VERBOSITY_NOVALUE = 3  # highest level, additional debug info

LOGFILE_DEFAULT = None
LOGFILE_NOVALUE = "game.log"

PKG_SPEC_HELP = """
The required positional arguments RED and BLUE are 'package specifications'.
These specify which Python package/module to import and search for a class
named 'Agent' (to instantiate for each player in the game). When we assess your
final program this will just be the top-level package 'agent' as per the
template given.

You may wish to play games with another agent class from a different package,
for example, while you develop your agent and want to compare different
approaches. To do this, use a absolute module name like used with ordinary
import statements, e.g. 'some_moule.agent2'.

By default, the referee will attempt to import the specified package/module and
then load a class named 'Agent'. If you want the referee to look for a class
with some other name you can put the alternative class name after a colon
symbol ':' (e.g. 'agent:DifferentAgent').
"""


def get_options():
    """Parse and return command-line arguments."""

    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description=DESCRIP,
        add_help=False,  # <-- we will add it back to the optional group.
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # positional arguments used for player agent package specifications:
    positionals = parser.add_argument_group(
        title="Basic usage",
        description=PKG_SPEC_HELP,
    )
    for num, col in enumerate(map(str, PlayerColor), 1):
        Col = col.title()
        positionals.add_argument(
            f"player{num}_loc",
            metavar=col,
            action=PackageSpecAction,
            help=f"location of {Col}'s player Agent class (e.g. package name)",
        )

    # optional arguments used for configuration:
    optionals = parser.add_argument_group(title="Optional arguments")
    optionals.add_argument(
        "-h",
        "--help",
        action="help",
        help="show this message.",
    )
    optionals.add_argument(
        "-V",
        "--version",
        action="version",
        version=VERSION,
    )
    
    optionals.add_argument(
        "-w",
        "--wait",
        metavar="wait",
        type=float,
        nargs="?",
        default=WAIT_DEFAULT,  # if the flag is not present
        const=WAIT_NOVALUE,  # if the flag is present with no value
        help="how long (float, seconds) to wait between game turns. 0: "
        "no delay; negative: wait for user input.",
    )

    optionals.add_argument(
        "-s",
        "--space",
        metavar="space_limit",
        type=float,
        nargs="?",
        default=SPACE_LIMIT_DEFAULT,
        const=SPACE_LIMIT_NOVALUE,
        help="limit on memory space (float, MB) for each agent.",
    )
    optionals.add_argument(
        "-t",
        "--time",
        metavar="time_limit",
        type=float,
        nargs="?",
        default=TIME_LIMIT_DEFAULT,
        const=TIME_LIMIT_NOVALUE,
        help="limit on CPU time (float, seconds) for each agent.",
    )

    verbosity_group = optionals.add_mutually_exclusive_group()
    verbosity_group.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="show extra debug level logs (equivalent to -v 3)",
    )
    verbosity_group.add_argument(
        "-v",
        "--verbosity",
        type=int,
        choices=range(0, VERBOSITY_LEVELS),
        nargs="?",
        default=VERBOSITY_DEFAULT,
        const=VERBOSITY_NOVALUE,
        help="control the level of output (not including output from "
        "agents). 0: no output except result; 1: commentary, but no"
        " board display; 2: (default) commentary and board display; "
        "3: (equivalent to -d) extra debug information.",
    )

    optionals.add_argument(
        "-l",
        "--logfile",
        type=str,
        nargs="?",
        default=LOGFILE_DEFAULT,
        const=LOGFILE_NOVALUE,
        metavar="LOGFILE",
        help="if you supply this flag the referee will redirect the log of "
        "all game actions to a text file named %(metavar)s "
        "(default: %(const)s).",
    )

    colour_group = optionals.add_mutually_exclusive_group()
    colour_group.add_argument(
        "-c",
        "--colour",
        action="store_true",
        help="force colour display using ANSI control sequences "
        "(default behaviour is automatic based on system).",
    )
    colour_group.add_argument(
        "-C",
        "--colourless",
        action="store_true",
        help="force NO colour display (see -c).",
    )

    unicode_group = optionals.add_mutually_exclusive_group()
    unicode_group.add_argument(
        "-u",
        "--unicode",
        action="store_true",
        help="force pretty display using unicode characters "
        "(default behaviour is automatic based on system).",
    )
    unicode_group.add_argument(
        "-a",
        "--ascii",
        action="store_true",
        help="force basic display using only ASCII characters (see -u).",
    )

    args = parser.parse_args()
    # post-processing to combine mutually exclusive options
    # debug => verbosity 3
    if args.debug:
        args.verbosity = 3
    del args.debug # type: ignore
    # colour, colourless => force colour(less), else auto-detect
    if args.colour:
        args.use_colour = True
    elif args.colourless:
        args.use_colour = False
    else:
        args.use_colour = sys.stdout.isatty() and sys.platform != "win32"
    del args.colour, args.colourless # type: ignore
    # unicode, ascii => force display mode unicode or ascii, else auto-detect
    if args.unicode:
        args.use_unicode = True
    elif args.ascii:
        args.use_unicode = False
    else:
        # quick and dirty check for unicode support as default
        try:
            '☺'.encode(sys.stdout.encoding)
            auto_use_unicode = True
        except UnicodeEncodeError:
            auto_use_unicode = False
        args.use_unicode = auto_use_unicode
    del args.unicode, args.ascii # type: ignore

    # done!
    if args.verbosity > 0:
        print(WELCOME)
    return args

@dataclass(frozen=True, order=True)
class PlayerLoc:
    """A player location specification."""
    pkg: str
    cls: str

    def __str__(self):
        return f"{self.pkg}:{self.cls}"
    
    def __iter__(self):
        yield self.pkg
        yield self.cls
        

class PackageSpecAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, str):
            raise argparse.ArgumentError(
                self, "expected a string, got %r" % (values,)
            )

        pkg_spec = values

        # detect alternative class:
        if ":" in pkg_spec:
            pkg, cls = pkg_spec.split(":", maxsplit=1)
        else:
            pkg = pkg_spec
            cls = "Agent"

        # try to convert path to module name
        mod = pkg.strip("/\\").replace("/", ".").replace("\\", ".")
        if mod.endswith(".py"):  # NOTE: Assumes submodule is not named `py`.
            mod = mod[:-3]

        # save the result in the arguments namespace as a PlayerLoc
        setattr(namespace, self.dest, PlayerLoc(mod, cls))
