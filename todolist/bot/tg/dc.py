from dataclasses import dataclass
from typing import List


@dataclass
class GetUpdateResponse:
    ok: bool
    result: List[UpdateObj]

    class Meta:
        unknown = EXCLUDE

@dataclass
class SendMessageResponse:
    ok: bool
    result: Message


