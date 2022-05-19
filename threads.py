from threading import Thread
from typing import Optional

from singleton import Singleton


class Threads(Singleton):
    _threads = dict[str: Thread]()

    def start(self, thread: Thread):
        self._threads[thread.name] = thread
        thread.start()

    def get(self, name: str) -> Optional[Thread]:
        return self._threads[name]

    def remove(self, name: str):
        self._threads[name] = None
