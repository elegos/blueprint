from typing import TypeVar


T = TypeVar('T')


def autoemit(name: str, signal_attr_name: str, type: T) -> T:
    attr_name = f'__{name}'

    def getter(self) -> T:
        return getattr(self, attr_name)

    def setter(self, new_value: T):
        setattr(self, attr_name, new_value)

        getattr(self, signal_attr_name).emit(new_value)

    return property(getter, setter)
