# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import gc
import time
from pathlib import Path


class ResourceLimitException(Exception):
    """For when agents exceed specified time / space limits."""


class CountdownTimer:
    """
    Reusable context manager for timing specific sections of code

    * measures CPU time, not wall-clock time
    * unless time_limit is 0, throws an exception upon exiting the context
      after the allocated time has passed
    """

    def __init__(self, time_limit, tolerance=1.0):
        """
        Create a new countdown timer with time limit `limit`, in seconds
        (0 for unlimited time). If `tolerance` is specified, the timer will
        allow the process to run for `tolerance` times the specified limit
        before throwing an exception.
        """
        self._limit = time_limit
        self._tolerance = tolerance
        self._clock = 0
        self._delta = 0

    def total(self):
        return self._clock

    def delta(self):
        return self._delta

    def __enter__(self):
        # clean up memory off the clock
        gc.collect()
        # then start timing
        self.start = time.process_time()
        return self  # unused

    def __exit__(self, exc_type, exc_val, exc_tb):
        # accumulate elapsed time since __enter__
        elapsed = time.process_time() - self.start
        self._clock += elapsed
        self._delta = elapsed

        # if we are limited, let's hope we aren't out of time!
        if self._limit is not None and self._limit > 0:
            if self._clock > self._limit * self._tolerance:
                raise ResourceLimitException(
                    f"exceeded available time"
                )


class MemoryWatcher:
    """
    Context manager for clearing memory before and measuring memory usage
    after using a specific section of code.

    * works by parsing procfs; only available on linux.
    * unless the limit is set to 0, throws an exception upon exiting the
      context if the memory limit has been breached
    """

    def __init__(self, space_limit, tolerance=1.0):
        self._limit = space_limit
        self._tolerance = tolerance
        self._curr_usage = -1
        self._peak_usage = -1

    def curr(self):
        return self._curr_usage

    def peak(self):
        return self._peak_usage

    def enabled(self):
        return _SPACE_ENABLED

    def __enter__(self):
        return self  # unused

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Check up on the current and peak space usage of the process, printing
        stats and ensuring that peak usage is not exceeding limits
        """
        if _SPACE_ENABLED:
            self._curr_usage, self._peak_usage = _get_space_usage()

            # adjust measurements to reflect usage of agents and referee, not
            # the Python interpreter itself
            self._curr_usage -= _DEFAULT_MEM_USAGE
            self._peak_usage -= _DEFAULT_MEM_USAGE

            # if we are limited, let's hope we are not out of space!
            if self._limit is not None and self._limit > 0:
                if self._peak_usage > self._limit * self._tolerance:
                    raise ResourceLimitException(
                        f"exceeded space limit (peak={self._peak_usage:.1f}MB)"
                    )


def _get_space_usage():
    """
    Find the current and peak Virtual Memory usage of the current process,
    in MB
    """
    # on linux, we can find the memory usage of our program we seek
    # inside /proc/self/status (specifically, fields VmSize and VmPeak)
    with Path("/proc/self/status").open() as proc_status:
        for line in proc_status:
            if "VmSize:" in line:
                curr_usage = int(line.split()[1]) / 1024  # kB -> MB
            elif "VmPeak:" in line:
                peak_usage = int(line.split()[1]) / 1024  # kB -> MB
    return curr_usage, peak_usage # type: ignore


_DEFAULT_MEM_USAGE = 0

_SPACE_ENABLED = False


def set_space_line():
    """
    by default, the python interpreter uses a significant amount of space
    measure this first to later subtract from all measurements
    """
    global _SPACE_ENABLED, _DEFAULT_MEM_USAGE

    try:
        _DEFAULT_MEM_USAGE, _ = _get_space_usage()
        _SPACE_ENABLED = True
    except:
        # this also gives us a chance to detect if our space-measuring method
        # will work on this platform, and notify the user if not.
        _SPACE_ENABLED = False
