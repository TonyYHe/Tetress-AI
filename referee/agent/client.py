# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import sys
from asyncio import subprocess, wait_for
from asyncio.subprocess import create_subprocess_exec, Process
from asyncio.exceptions import TimeoutError as AIOTimeoutError
from typing import Any

from ..log import NullLogger, LogStream
from .resources import ResourceLimitException
from .io import AsyncProcessStatus, m_pickle, m_unpickle,\
    _SUBPROC_MODULE, _ACK, _REPLY_OK, _REPLY_EXC, _CHUNK_LIMIT_KB

class WrappedProcessException(Exception):
    pass

# Context manager that wraps a class in a separate "sandbox" process. The class
# is instantiated in the subprocess, and all calls to methods are forwarded to
# the subprocess. Exceptions are also forwarded back to the parent process. 

class RemoteProcessClassClient:

    def __init__(self, 
        pkg: str, cls: str, 
        time_limit: float | None, space_limit: float | None,
        res_limit_tolerance: float,
        recv_timeout: float, # Hard timeout (s) for receiving a reply
        subproc_output: bool,
        *cons_args, 
        log: LogStream=NullLogger(),
        **cons_kwargs
    ):
        self._pkg = pkg
        self._cls = cls
        self._time_limit = time_limit
        self._space_limit = space_limit
        self._res_limit_tolerance = res_limit_tolerance
        self._recv_timeout = recv_timeout
        self._subproc_output = subproc_output
        self._log = log
        self._cons_args = cons_args
        self._cons_kwargs = cons_kwargs
        self._proc: Process | None = None
        self._status: AsyncProcessStatus | None = None
        self._killed: bool = False

    @property
    def pid(self) -> int:
        assert self._proc is not None
        return self._proc.pid

    @property
    def status(self) -> AsyncProcessStatus | None:
        return self._status

    async def _recv_reply(self):
        assert self._proc is not None
        assert self._proc.stdout is not None
        # Read reply from subprocess (with hard timeout)
        self._log.debug(
            f"waiting for reply from subprocess {self._proc.pid} (stdout)")
        try:
            line = await wait_for(
                self._proc.stdout.readline(),
                timeout=self._recv_timeout
            )
        except AIOTimeoutError as e:
            # Process hasn't replied for a long time, kill it
            self._log.debug(
                f"reply not received within {self._recv_timeout}s!")
            await self._kill()
            raise ResourceLimitException(
                f"subprocess message recv time limit "
                f"({self._recv_timeout}s) exceeded"
            ) from e

        if not line:
            raise EOFError("expected result, got EOF")

        return await self._process_reply(m_unpickle(line))

    async def _process_reply(self, reply: tuple[Any, ...]):
        assert self._proc is not None

        status, *args = reply
        self._status = status
        match args:
            case (_REPLY_EXC, ResourceLimitException() as e, _):
                raise e
            case (_REPLY_EXC, Exception() as e, stacktrace_str):
                raise WrappedProcessException(
                    f"exception in process: {self._proc.pid}\n",
                    {
                        "exception_type": e.__class__.__name__,
                        "exception_msg": str(e),
                        "stacktrace_str": stacktrace_str,
                    }
                )
            case (_REPLY_OK, result):
                return result
            case _:
                raise ValueError(f"unexpected reply: {reply}")

    async def _graceful_exit(self):
        assert self._proc is not None
        assert self._proc.stdin is not None

        # Gracefully end process by writing EOF to stdin
        self._log.debug(
            f"gracefully ending subprocess {self._proc.pid}...")
        self._proc.stdin.write_eof()
        await self._proc.wait()

    async def _kill(self):
        assert self._proc is not None
        self._log.debug(f"killing subprocess {self._proc.pid}")
        self._proc.kill()
        await self._proc.wait()
        self._killed = True

    async def __aenter__(self):
        # Start subprocess
        self._proc = await create_subprocess_exec(
            sys.executable, "-m", _SUBPROC_MODULE,
            m_pickle((
                self._pkg, self._cls,
                self._time_limit, self._space_limit,
                self._res_limit_tolerance,
                self._cons_args, 
                self._cons_kwargs
            )),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL if not self._subproc_output else None,
            limit = _CHUNK_LIMIT_KB * 1000
        )
        assert self._proc is not None
        assert self._proc.stdin is not None
        self._log.debug(f"subprocess {self._proc.pid} started")
        
        # Expect ack that constructor was called
        try:
            self._log.debug(
                f"initialising class '{self._pkg}:{self._cls}' "
                f"on subprocess {self._proc.pid}"
            )
            assert await self._recv_reply() == _ACK
        except:
            # Exception during construction occured
            self._log.debug(
                f"exception occured during construction of class"
            )
            await self._graceful_exit()
            raise
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        assert self._proc is not None
        assert self._proc.stdin is not None

        if exc_type is not None:
            self._log.debug(f"an exception occured!")

        if not self._killed:
            # Gracefully end process by writing EOF to stdin
            await self._graceful_exit()

        # Check for errors
        if self._proc.returncode != 0 and not self._killed:
            raise RuntimeError(f"subprocess exited with code "
                               f"{self._proc.returncode}")

    # Support "transparent" method calls on subprocess class instance
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        async def call(*args, **kwargs):
            assert self._proc is not None
            assert self._proc.stdin is not None
            assert self._proc.stdout is not None

            # Send method call, wait for result
            self._log.debug(
                f"send method call request to subprocess "
                f"{self._proc.pid} (stdin)"
            )
            self._proc.stdin.write(m_pickle((name, args, kwargs)))
            return await self._recv_reply()

        return call
