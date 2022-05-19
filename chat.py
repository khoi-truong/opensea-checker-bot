from enum import Enum
from typing import Optional

from persistent import Persistent
from telegram import Chat

import config


class ChatType(Enum):
    PRIVATE = 'private'
    GROUP = 'group'


class ChatInfo(Persistent):
    id: str
    type: ChatType
    username: str

    def __init__(self, chat: Chat, username: str):
        self.id = chat.id
        self.type = ChatType(chat.type)
        self.username = username

    def __get_group_username(self) -> Optional[str]:
        if self.type == ChatType.GROUP:
            return f"@{self.username}"
        return None

    def debug_str(self, indent: int = 0) -> str:
        indent_str = '    ' * indent
        return f"""{{
    {indent_str}"id": "{self.id}",
    {indent_str}"type": "{self.type.value}",
    {indent_str}"username": "{self.username}"
{indent_str}}}"""

    def debug(self):
        if config.DEBUG:
            print(f"""ChatInfo: {self.debug_str(indent=1)}""")

    group_username = property(__get_group_username)
