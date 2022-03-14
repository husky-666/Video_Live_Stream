"""
utils.play_enum
状态枚举
"""
from enum import Enum


class PlayMethod(Enum):
    """
    播放模式。
    + NEXT    : 顺序播放
    + PREV    : 逆序播放
    + REPEAT  : 重复播放
    """
    NEXT = "N"
    PREV = "P"
    REPEAT = "R"


class ListLoopState(Enum):
    """
    播放列表循环标识。
    + LOOP_KEEP   : 继续循环
    + LOOP_BREAK  : 跳出循环
    """
    LOOP_KEEP = 1
    LOOP_BREAK = 0
