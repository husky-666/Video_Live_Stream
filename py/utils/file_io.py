"""
utils.file_io
文件读写的简单封装
"""
import json
from typing import List


def text_write(path: str, text: str) -> None:
    """
    清空文件内容后写入文本
    :param path: 文件路径
    :param text: 写入文本内容
    :return: None
    """
    with open(path, mode='w', encoding='utf-8') as f:
        f.write(text)
        f.flush()


def text_read(path: str) -> List[str]:
    """
    以文本形式读取文件内容
    :param path: 文件路径
    :return: list
    """
    with open(path, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
        return lines


def json_load(path: str) -> dict:
    """
    读取文件，JSON对象转换为字典类型
    :param path: 文件路径
    :return: dict
    """
    with open(path, mode='r', encoding='utf-8') as f:
        return json.load(f)
