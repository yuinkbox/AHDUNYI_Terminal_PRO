import re

ROOM_ID_PATTERN: str = r'(?:\u9765\s*|ID[:\uff1a]\s*)?(\d{3,10})'
ROOM_ID_RE: re.Pattern = re.compile(ROOM_ID_PATTERN)
