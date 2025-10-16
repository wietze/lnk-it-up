from enum import IntEnum
from functools import reduce
from typing import TypeVar


class ByteTools:
    T = TypeVar('T', bound=IntEnum)

    @staticmethod
    def create_bytes(integer: int, size: int) -> bytes:
        return integer.to_bytes(size, 'little')

    @staticmethod
    def resolve(input: list[T]) -> int:
        if not input:
            return 0
        return reduce(lambda x, y: x | y, input)

    @staticmethod
    def bytearray(input: list[int]) -> bytes:
        return b''.join([ByteTools.create_bytes(char, 1) for char in input])
