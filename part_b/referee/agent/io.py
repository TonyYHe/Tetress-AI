# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

import binascii
from contextlib import contextmanager
import pickle
from dataclasses import dataclass
from binascii import b2a_base64, a2b_base64
from typing import Any


_SUBPROC_MODULE = "referee.agent.subprocess"
_ACK = "ACK"
_REPLY_OK = b"OK"
_REPLY_EXC = b"EXC"
_CHUNK_LIMIT_KB = 1024


class InterchangeException(Exception):
    pass


@dataclass(frozen=True, slots=True, init=True)
class AsyncProcessStatus:
    time_delta: float
    time_used: float
    space_known: bool
    space_curr: float
    space_peak: float


@contextmanager
def catch_exceptions(op: str, data: Any):
    try:
        yield
    except pickle.PicklingError as e:
        raise InterchangeException(
            f"cannot {op} object: {data}") from e
    except binascii.Error as e:
        raise InterchangeException(
            f"expecting b64 during {op} but got: \n{data}") from e

def m_pickle(o: Any) -> bytes:
    with catch_exceptions("pickle", o):
        return b2a_base64(pickle.dumps(o))

def m_unpickle(b: bytes) -> Any:
    with catch_exceptions("unpickle", b):
        return pickle.loads(a2b_base64(b))
