from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

class OnSendRecv(Enum):
    SEND = 1
    RECV = 2

@dataclass()
class EListener(object):
    opcode:int
    callback:callable = None
    callback_arguments:Optional[Tuple] = None
    first_argument_packet = True