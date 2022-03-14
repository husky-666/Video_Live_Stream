"""
bilibili_live.aiorequest
网络连接
"""
import aiohttp
import asyncio
from atexit import register

__session: aiohttp.ClientSession = None


@register
def __clean_session():
    """
    程序退出清理session。
    """
    if __session is None or __session.closed:
        return
    asyncio.get_event_loop().run_until_complete(__session.close())


def get_session():
    global __session
    if __session is None:
        __session = aiohttp.ClientSession()
    return __session


def set_session(session: aiohttp.ClientSession):
    global __session
    __session = session
    return __session


async def request(method: str = None, url: str = None, data=None, headers=None, cookies=None):
    async with get_session().request(method=method, url=url, data=data, headers=headers, cookies=cookies) as response:
        try:
            # 检查状态码
            response.raise_for_status()
        except:
            raise
        if response.content_length == 0:
            return None
        if response.content_type.lower().find("application/json") == -1:
            raise Exception("content_type is not application/json")

        return await response.json()
