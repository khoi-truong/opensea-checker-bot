from copy import deepcopy
from functools import reduce
from typing import Any, Optional

import config
from asset import Asset
from chat import ChatInfo
from singleton import Singleton


class Storage(Singleton):
    _root: dict[str, Any] = {
        'asset_chats': dict[str, ChatInfo](),
        'assets': dict[str, Asset](),
        'users': list[str]()
    }

    def get_asset_chats(self) -> dict[str, ChatInfo]:
        return self._root['asset_chats']

    def set_asset_chats(self, asset_chats: dict[str: ChatInfo]()):
        self._root['asset_chats'] = deepcopy(asset_chats)

    def get_chat(self, key: str) -> Optional[ChatInfo]:
        asset_chats: dict[str, ChatInfo] = self._root['asset_chats']
        chat = asset_chats.get(key)
        return chat

    def set_chat(self, key: str, chat: ChatInfo):
        asset_chats: dict[str, ChatInfo] = self._root['asset_chats']
        asset_chats.update({deepcopy(key): deepcopy(chat)})
        self._root.update({'asset_chats': asset_chats})

    def remove_chat(self, key: str):
        self.pop_chat(key)

    def pop_chat(self, key: str) -> Optional[ChatInfo]:
        asset_chats: dict[str, ChatInfo] = self._root['asset_chats']
        chat = asset_chats.pop(key, None)
        self._root.update({'asset_chats': asset_chats})
        return chat

    def get_assets(self) -> dict[str, Asset]:
        return self._root['assets']

    def set_assets(self, assets: dict[str: Asset]()):
        self._root['assets'] = deepcopy(assets)

    def get_asset(self, key: str) -> Optional[Asset]:
        assets: dict[str, Asset] = self._root['assets']
        asset = assets.get(key)
        return asset

    def set_asset(self, key: str, asset: Asset):
        assets: dict[str, Asset] = self._root['assets']
        assets.update({deepcopy(key): deepcopy(asset)})
        self._root.update({'assets': assets})

    def remove_asset(self, key: str):
        self.pop_asset(key)

    def pop_asset(self, key: str) -> Optional[Asset]:
        assets: dict[str, Asset] = self._root['assets']
        asset = assets.pop(key, None)
        self._root.update({'assets': assets})
        return asset

    def get_users(self) -> [str]:
        return self._root['users']

    def set_users(self, users: list[str]):
        self._root['users'] = deepcopy(users)

    def debug_str(self) -> str:
        asset_chats = ''
        for key, value in self.asset_chats.items():
            asset_chats = asset_chats + \
                f"""\n        "{key}": {value.debug_str(indent=2)}"""
        assets = ''
        for key, value in self.assets.items():
            assets = assets + \
                f"""\n        "{key}": {value.debug_str(indent=2)}"""
        return f"""{{
    "users": [
        {reduce(lambda x, y: f'{x}, "{y}"', self.users, '').removeprefix(', ')}
    ],
    "asset_chats": {{{asset_chats}
    }},
    "assets": {{{assets}
    }}
}}"""

    def debug(self):
        if config.DEBUG:
            print(f"Storage: {self.debug_str()}")

    asset_chats = property(get_asset_chats, set_asset_chats)
    assets = property(get_assets, set_assets)
    users = property(get_users, set_users)
