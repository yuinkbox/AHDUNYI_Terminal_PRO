from dataclasses import dataclass
from typing import Optional

@dataclass
class TokenPayload:
    username: str
    role: str
    user_id: Optional[int] = None
    exp: Optional[int] = None
