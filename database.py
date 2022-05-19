import os
from copy import deepcopy
from threading import Thread
from typing import Any

import transaction
import ZODB
import ZODB.FileStorage
from BTrees.OOBTree import BTree

from singleton import Singleton
from storage import Storage


class DatabaseThread(Thread):
    should_dump = False

    def __init__(self):
        Thread.__init__(self, name='DB')

    def run(self):
        root = DatabaseThread.open()
        while True:
            if self.should_dump:
                root.users = Storage().users
                root.asset_chats = BTree()
                root.assets = BTree()
                for key in Storage().asset_chats.keys():
                    chat = Storage().get_chat(key)
                    root.asset_chats[key] = deepcopy(chat)
                for key in Storage().assets.keys():
                    asset = Storage().get_asset(key)
                    root.assets[key] = deepcopy(asset)
                transaction.commit()
                self.should_dump = False

    @staticmethod
    def open() -> Any:
        path = os.path.dirname(__file__)
        db = ZODB.DB(ZODB.FileStorage.FileStorage(f'{path}/zodb'))
        connection = db.open()
        root = connection.root()
        try:
            root.asset_chats
        except AttributeError:
            root.asset_chats = BTree()
            print("INFO: 'root' object has no attribute 'asset_chats'. "
                  "'root.asset_chats' will be initialized by default.")
        except Exception as e:
            print(e)
        try:
            root.assets
        except AttributeError:
            root.assets = BTree()
            print("INFO: 'root' object has no attribute 'assets'. "
                  "'root.assets' will be initialized by default.")
        except Exception as e:
            print(e)
        try:
            root.users
        except AttributeError:
            root.users = list[str]()
            print("INFO: 'root' object has no attribute 'users'. "
                  "'root.users' will be initialized by default.")
        except Exception as e:
            print(e)
        Storage().users = root.users
        for key in root.asset_chats.keys():
            chat = root.asset_chats.get(key)
            Storage().set_chat(key, chat)
        for key in root.assets.keys():
            asset = root.assets.get(key)
            Storage().set_asset(key, asset)
        Storage().debug()
        transaction.commit()
        return root


class Database(Singleton):
    thread = DatabaseThread()

    def open(self):
        self.thread.start()

    def dump(self):
        self.thread.should_dump = True
