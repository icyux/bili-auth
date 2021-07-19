#!/bin/python3

import time
import threading
import random


def check(pool, times=20, maxCount=5):
    while len(pool.expire) >= times:
        count = 0
        for k in random.sample(list(pool.expire), times):
            if not pool.get(k):
                count += 1
        if count < maxCount:
            break


def expireTest(pool, cycle):
    try:
        while pool:
            check(pool)
            time.sleep(cycle)
    except NameError:
        pass
    finally:
        del pool


class Pool:
    def __init__(self, *, checkCycle=10):
        self.alive = True
        self.__pool = {}
        self.expire = {}
        t = threading.Thread(target=lambda: expireTest(self, checkCycle))
        t.daemon = True
        t.start()

    def get(self, key):
        if self.expire.get(key) and self.expire[key] <= int(time.time()):
            self.delete(key)
            return None
        return self.__pool.get(key)

    def set(self, key, value, *, expire: int = None):
        self.__pool[key] = value
        if expire:
            self.expire[key] = int(time.time()) + expire
        elif self.expire.get(key):
            self.expire.pop(key)

    def delete(self, key):
        if self.expire.get(key):
            self.expire.pop(key)
        if self.__pool.get(key):
            return bool(self.__pool.pop(key))
