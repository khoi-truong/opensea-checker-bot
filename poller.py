import time
from threading import Thread
from typing import Optional

from telegram import Bot

import config
from asset import Asset, AssetIdentifier, to_asset_identifier
from asset_requests import get_asset, get_created_event
from database import Database
from messenger import Messenger
from singleton import Singleton
from storage import Storage
from threads import Threads


class PollingAssetThread(Thread):
    identifier: AssetIdentifier
    bot: Bot
    asset: Optional[Asset] = None
    should_terminate: bool = False

    def __init__(self, identifier: AssetIdentifier, bot: Bot, asset: Optional[Asset] = None):
        Thread.__init__(self, name=PollingAssetThread.get_thread_name(
            identifier), daemon=True)
        self.identifier = identifier
        self.bot = bot
        self.asset = asset

    def run(self):
        while True:
            if self.should_terminate:
                return
            key = self.identifier.to_str()
            if key not in Storage().asset_chats.keys():
                return
            time.sleep(config.INTERVAL)
            event = get_created_event(self.identifier)
            chat = Storage().get_chat(key)
            if chat is None:
                return
            messenger = Messenger(bot=self.bot, chat=chat)
            if event is not None:
                if self.asset is None:
                    self.asset = get_asset(self.identifier)
                messenger.notify_created_asset(asset=self.asset)
                Storage().pop_chat(key)
                Database().dump()
                return
            else:
                messenger.debug(self.identifier)

    @staticmethod
    def get_thread_name(identifier: AssetIdentifier) -> str:
        return f'Asset: {identifier.to_str()}'


class ResumePollingAssetThread(Thread):
    bot: Bot

    def __init__(self, bot: Bot):
        Thread.__init__(self, name='Resume Polling')
        self.bot = bot

    def run(self):
        Database().open()
        time.sleep(1)
        keys = Storage().asset_chats.keys()
        for key in list(keys):
            chat = Storage().get_chat(key)
            identifier = to_asset_identifier(key)
            asset = get_asset(identifier)
            messenger = Messenger(bot=self.bot, chat=chat)
            if asset is None:
                messenger.notify_not_found_asset(identifier, resume=True)
            else:
                messenger.notify_not_created_asset(asset, resume=True)
            AssetPoller().start_polling_asset(identifier, asset)


class AssetPoller(Singleton):
    _bot: Optional[Bot]

    def start_polling_asset(self, identifier: AssetIdentifier, asset: Optional[Asset] = None):
        if self._bot is None:
            return
        thread = PollingAssetThread(
            identifier=identifier, bot=self._bot, asset=asset)
        Threads().start(thread)

    def set_bot(self, bot: Bot):
        self._bot = bot

    @staticmethod
    def stop_polling_asset(identifier: AssetIdentifier):
        thread = Threads().get(PollingAssetThread.get_thread_name(identifier))
        thread.should_terminate = True
