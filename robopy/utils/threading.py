from threading import Semaphore


class List(list):
    def __init__(self):
        super().__init__()
        self.__semaphore: Semaphore = Semaphore()
        self.__atomic_statement: bool = False

    def __enter__(self):
        self.__semaphore.acquire()
        self.__atomic_statement = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__atomic_statement = False
        self.__semaphore.release()

    def __acquire(self):
        if not self.__atomic_statement:
            self.__semaphore.acquire()

    def __release(self):
        if not self.__atomic_statement:
            self.__semaphore.release()

    def append(self, p_object):
        self.__acquire()
        super().append(p_object)
        self.__release()

    def clear(self):
        self.__acquire()
        super().clear()
        self.__release()

    def copy(self):
        self.__acquire()
        result = super().copy()
        self.__release()
        return result

    def count(self, value):
        self.__acquire()
        result = super().count(value)
        self.__release()
        return result

    def extend(self, iterable):
        self.__acquire()
        super().extend(iterable)
        self.__release()

    def index(self, value, start=None, stop=None):
        self.__acquire()
        result = super().index(value, start=start, stop=stop)
        self.__release()
        return result

    def insert(self, index, p_object):
        self.__acquire()
        super().insert(index, p_object)
        self.__release()

    def pop(self, index=None):
        self.__acquire()
        result = super().pop(index=index)
        self.__release()
        return result

    def remove(self, value):
        self.__acquire()
        super().remove(value)
        self.__release()

    def reverse(self):
        self.__acquire()
        super().reverse()
        self.__release()

    def sort(self, key=None, reverse=False):
        self.__acquire()
        super().sort(key=key, reverse=reverse)
        self.__release()
