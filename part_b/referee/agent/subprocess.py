# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import sys
from contextlib import contextmanager
from importlib import import_module
from importlib.util import find_spec
from traceback import format_exc
from typing import Any

from .resources import CountdownTimer, MemoryWatcher, set_space_line
from .io import AsyncProcessStatus, m_pickle, m_unpickle,\
    _ACK, _REPLY_OK, _REPLY_EXC

_STDOUT_OVERRIDE_MESSAGE = "stdout usage is not allowed in agent (use stderr)"
_STDIN_OVERRIDE_MESSAGE = "stdin usage is not allowed in agent"


# Wrapper subprocess entry point
def main():
    in_stream = sys.stdin
    out_stream = sys.stdout

    # Redirect stdout to stderr (debugging purposes). This allows for seamless
    # use of print() in the subprocess without interruping data interchange
    # with the parent process.
    sys.stdout = sys.stderr

    # Explicitly override __stdout__ to raise an exception if it is used (this
    # is a hack to prevent the subprocess from using stdout, which is used for
    # data interchange with the parent process)
    class _StdoutOverride:
        def write(self, *args, **kwargs):
            raise RuntimeError(_STDOUT_OVERRIDE_MESSAGE)

        def flush(self, *args, **kwargs):
            raise RuntimeError(_STDOUT_OVERRIDE_MESSAGE)

    sys.__stdout__ = _StdoutOverride()

    # Same for stdin
    class _StdinOverride:
        def read(self, *args, **kwargs):
            raise RuntimeError(_STDIN_OVERRIDE_MESSAGE)
                
        def readline(self, *args, **kwargs):
            raise RuntimeError(_STDIN_OVERRIDE_MESSAGE)

        def readlines(self, *args, **kwargs):
            raise RuntimeError(_STDIN_OVERRIDE_MESSAGE)

    sys.__stdin__ = _StdinOverride()
    sys.stdin = _StdinOverride()

    # Utils
    def _s_unpickle(s: str) -> Any:
        return m_unpickle(bytes(s, "ascii"))

    def _s_pickle(o: Any) -> str:
        return m_pickle(o).decode("ascii")
    
    def _is_pickleable(o: Any) -> bool:
        try:
            m_pickle(o)
            return True
        except Exception:
            return False

    # Command line arguments are the class/constructor arguments
    cls_module, cls_name, \
        time_limit, space_limit, \
        res_limit_tolerance, \
        cons_args, cons_kwargs \
        = _s_unpickle(sys.argv[1])

    # Create some context managers for resource tracking
    timer = CountdownTimer(time_limit, res_limit_tolerance)
    space = MemoryWatcher(space_limit, res_limit_tolerance)

    def _get_status():
        return AsyncProcessStatus(
            time_delta=timer.delta(),
            time_used=timer.total(),
            space_known=space.enabled(),
            space_curr=space.curr(),
            space_peak=space.peak(),
        )

    def _referee():
        time_rem = time_limit - timer.total() if time_limit > 0 else None
        space_rem = space_limit - space.curr() if space.curr() > 0 else None
        if space.enabled() and space.curr() == -1:
            # No space used yet, so we can't know how much space is left
            space_rem = space_limit if space_limit > 0 else None 
        return {
            "time_remaining": time_rem,
            "space_remaining": space_rem,
            "space_limit": space_limit if space_limit > 0 else None,
        }

    # Comms functions
    def _recv() -> Any:
        line = in_stream.readline()
        if not line: # EOF, process should exit (see __aexit__ above)
            exit(0)
        return _s_unpickle(line)

    def _reply(*args: Any):
        # Reply is a tuple of (status, arg0, arg1, ...)
        out_stream.write(_s_pickle((_get_status(), *args)))
        out_stream.flush()

    @contextmanager
    def _relay_exceptions():
        try:
            yield
        except Exception as e:
            stacktrace_str = "\n".join(format_exc().splitlines()[5:])
            _reply(_REPLY_EXC, e, stacktrace_str)

    # If numpy exists on system, ensure it's imported so that it is included
    # in baseline memory usage calculations
    if find_spec("numpy") is not None and cls_name != "MockClient":
        import numpy

    # Construct class instance
    with _relay_exceptions(), timer, space:
        set_space_line()
        Cls = getattr(import_module(cls_module), cls_name)
        instance = Cls(*cons_args, **{**cons_kwargs, **_referee()})
    _reply(_REPLY_OK, _ACK)

    # Main client subprocess loop
    while True:
        message = _recv()
        name, args, kwargs = message
        
        # Call method
        result = None
        with _relay_exceptions(), timer, space:
            result = getattr(instance, name)(*args, **{**kwargs, **_referee()})
            if not _is_pickleable(result):
                result = "<unpickleable>"
        
        _reply(_REPLY_OK, result)

# Only run if directly invoked
if __name__ == "__main__" and sys.argv[0].endswith(__file__):
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
