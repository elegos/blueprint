from typing import Type, TypeVar

T = TypeVar('T')


class Singleton:
    __instances = {}

    def __new__(cls: Type[T], *args, **kwargs) -> T:
        key = cls.__module__ + '.' + cls.__name__
        if key not in Singleton.__instances:
            Singleton.__instances[key] = super().__new__(
                cls, *args, **kwargs)

        return Singleton.__instances[key]

    def __init__(self, *args, **kwargs) -> T:
        if hasattr(self, '_Singleton__initialized'):
            return

        self.__initialized = True
        super().__init__(*args, **kwargs)
