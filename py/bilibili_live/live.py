"""
bilibili_live.live
直播间WebSocket连接与弹幕发送
"""
import asyncio
import aiohttp
import struct
import json
import brotli
import time
from typing import Coroutine
from struct import Struct
from . import aiorequest


class Event:
    """
    事件类
    """
    def __init__(self, event_name: str, data: any):
        self.__event_name = event_name
        self.__data = data

    def getEvent_name(self):
        return self.__event_name

    def getData(self):
        return self.__data


class EventTarget:
    """
    发布-订阅模式异步事件支持类
    """
    def __init__(self):
        self.__listeners = {}

    def addEventListener(self, event_name: str, callback: Coroutine):
        """
        注册事件监听器。
        :param event_name:事件名称。
        :param callback:回调函数。
        :return:None。
        """
        if event_name not in self.__listeners:
            self.__listeners[event_name] = []
        self.__listeners[event_name].append(callback)

    def removeEventListener(self, event_name: str, callback: Coroutine):
        """
        移除事件监听函数。
        :param event_name:事件名称。
        :param callback:回调函数。
        :return:None。
        """
        if event_name not in self.__listeners:
            return
        if callback in self.__listeners[event_name]:
            self.__listeners[event_name].remove(callback)

    def dispatchEvent(self, event: Event):
        """
        分发事件
        :param event: 事件类。
        :return: None。
        """
        event_name = event.getEvent_name()
        if event_name not in self.__listeners:
            return
        data = event.getData()
        for callback in self.__listeners[event_name]:
            asyncio.create_task(callback(data))

    def on(self, event_name: str):
        """
        装饰器注册事件监听器
        :param event_name: 事件名称。
        """
        def decorator(func: Coroutine):
            self.addEventListener(event_name, func)
            return func

        return decorator


class RoomCollection(EventTarget):
    """
    直播间连接类
    """
    def __init__(self, roomid: int, head_struct_str: str = '>IHHII'):
        super().__init__()
        self.__roomid = roomid
        self.__head_struct = Struct(head_struct_str)
        self.__json_certification_utf8 = json.dumps(
            {
                "uid": 0,
                "roomid": roomid,
                "protover": 3,
                "platform": "web",
                "type": 2,
                "key": ""
            }).encode()
        self.__timer = None
        self.__task = []

    def __pack(self, packet_len: int, head_len: int,
               packet_ver: int, packet_type: int,
               num: int, data: bytes):
        """
        打包函数，按固定头部格式打包数据
        :return:bytes
        """
        return self.__head_struct.pack(packet_len, head_len,
                                       packet_ver, packet_type,
                                       num) + data

    def __decorator_unpack(func):
        """
        装饰器用于处理接收的数据
        """
        def unpack(self, packet: bytes):
            """
            解包函数
            :param packet: 二进制数据。
            :return: None。
            """
            result = []
            data = {}
            offset = 0
            while offset < len(packet):
                tup_head = self.__head_struct.unpack(packet[offset:offset + 16])
                if tup_head[2] == 3:
                    # 压缩过的数据需要解压处理
                    box = brotli.decompress(packet[offset + 16:])
                    offset_dec = 0
                    while offset_dec < len(box):
                        tup_head_dec = self.__head_struct.unpack(box[offset_dec:offset_dec + 16])
                        data = {
                            "packet_len": tup_head_dec[0],
                            "head_len": tup_head_dec[1],
                            "packet_ver": tup_head_dec[2],
                            "packet_type": tup_head_dec[3],
                            "num": tup_head_dec[4],
                            "data": json.loads(box[offset_dec + 16:offset_dec + tup_head_dec[0]].decode())
                        }
                        result.append(data)
                        offset_dec += tup_head_dec[0]
                else:
                    data = {
                        "packet_len": tup_head[0],
                        "head_len": tup_head[1],
                        "packet_ver": tup_head[2],
                        "packet_type": tup_head[3],
                        "num": tup_head[4],
                        "data": None
                    }
                    if tup_head[3] == 3:
                        # 心跳包反馈，提取人气值
                        data["data"] = {"view": struct.unpack('>I', packet[offset + 16:offset + 20])[0]}
                    else:
                        data["data"] = json.loads(packet[offset + 16:offset + tup_head[0]].decode())
                    result.append(data)
                offset += tup_head[0]

            func(self, result)

        return unpack

    @__decorator_unpack
    def __handleMessage(self, result: list):
        """
        数据分发处理函数
        :param result: 待分发的数据列表。
        """
        for packet in result:
            if packet["packet_type"] == 5:
                if packet["data"]["cmd"].startswith("DANMU_MSG"):
                    self.dispatchEvent(Event(event_name="DANMU_MSG", data=packet["data"]))
                else:
                    self.dispatchEvent(Event(event_name=packet["data"]["cmd"], data=packet["data"]))
            elif packet["packet_type"] == 8:
                # 认证回应
                if packet["data"]["code"] == 0:
                    # 认证成功
                    self.dispatchEvent(Event(event_name="CERTIFY_SUCCESS", data=packet["data"]))
            elif packet["packet_type"] == 3:
                # 心跳包回应
                self.dispatchEvent(Event(event_name="VIEW", data=packet["data"]))
                self.__timer = 30
            else:
                pass

    def __getCertification(self):
        """
        获取用于加入直播间的bytes类型的认证数据
        :return:bytes
        """
        return self.__pack(16 + len(self.__json_certification_utf8),
                           16, 1, 7, 1, self.__json_certification_utf8)

    async def __send_heartbeat(self, ws: aiohttp.client.ClientWebSocketResponse):
        """
        发送心跳包
        :param ws: ClientWebSocketResponse。
        :return: None。
        """
        try:
            while True:
                if self.__timer == 0:
                    await ws.send_bytes(self.__head_struct.pack(0, 16, 1, 2, 1))
                elif self.__timer <= -30:
                    raise Exception('timeout')
                await asyncio.sleep(1)
                self.__timer -= 1
        except asyncio.CancelledError:
            print("cancel Task-send_heartbeat")
            raise
        except:
            print("Task-send_heartbeat Error")
            raise

    async def __receive_data(self, ws: aiohttp.client.ClientWebSocketResponse):
        """
        接收二进制数据
        :param ws: ClientWebSocketResponse。
        :return: None。
        """
        try:
            while True:
                async for msg in ws:
                    if msg.data is not None:
                        self.__handleMessage(msg.data)
                await ws.close()
                raise Exception("连接中断")
        except asyncio.CancelledError:
            print("cancel Task-receive_data")
            raise
        except:
            print("Task-receive_data Error")
            raise

    async def startup(self, uri: str, timeout: int = 3):
        """
        入口函数
        :param uri: WebSocket地址。
        :param timeout: 断开重连时间（单位：秒）。
        :return: None。
        """
        print("-----房间 {room_id} 准备连接-----".format(room_id=self.__roomid))
        while True:
            self.__timer = 30
            async with aiorequest.get_session().ws_connect(uri) as ws:
                print("-----房间 {room_id} 已建立连接-----".format(room_id=self.__roomid))

                @self.on("CERTIFY_SUCCESS")
                async def on_certify_success(msg):
                    print("认证成功")
                    self.__task.append(asyncio.create_task(self.__send_heartbeat(ws)))

                await ws.send_bytes(self.__getCertification())
                self.__task.append(asyncio.create_task(self.__receive_data(ws)))
                while len(self.__task) < 2:
                    await asyncio.sleep(0.5)
                self.removeEventListener("CERTIFY_SUCCESS", on_certify_success)

                try:
                    await asyncio.gather(self.__task[0], self.__task[1])
                except Exception as err:
                    print("Error:", err)
                    self.__task[0].cancel()
                    self.__task[1].cancel()
                finally:
                    print("{time}秒后重连".format(time=str(timeout)))
                    await asyncio.sleep(timeout)
                    self.__task.clear()
                    print("-----准备重新连接-----")


class Cookies:
    """
    Cookies类，用于身份认证

    """
    def __init__(self, sessdata: str = None, buvid3: str = None, bili_jct: str = None):
        """
        :param sessdata:cookie中的SESSDATA。
        :param buvid3:cookie中的buvid3。
        :param bili_jct:cookie中的bili_jct。
        """
        self.sessdata = sessdata
        self.buvid3 = buvid3
        self.bili_jct = bili_jct

    def get_cookies(self) -> dict:
        """
        获取字典格式cookie
        :return:dict。
        """
        return {"SESSDATA": self.sessdata,
                "buvid3": self.buvid3,
                "bili_jct": self.bili_jct}


class BulletChat:
    def __init__(self,
                 bubble: int = 0,
                 msg: str = None,
                 color: int = int("FFFFFF", 16),
                 mode: int = 1,
                 fontsize: int = 25):
        """
        :param bubble:功能未知，默认0。
        :param msg:弹幕内容，长度需不大于30。
        :param color:字体颜色。
        :param mode:弹幕模式。
        :param fontsize:字体大小。
        :param roomid:房间号。
        """
        self.bubble = bubble
        self.msg = msg
        self.color = color
        self.mode = mode
        self.fontsize = fontsize


class RoomOperation:
    def __init__(self, roomid: int):
        self.__roomid = str(roomid)

    async def send_bulletchat(self,
                              url: str = "https://api.live.bilibili.com/msg/send",
                              bulletchat: BulletChat = None,
                              cookies: Cookies = None) -> dict:
        """
        :param url:发送弹幕url。
        :param bulletchat:BulletChat对象。
        :param cookies:Cookies对象。
        """
        method = "POST"
        headers = {"referer": "https://live.bilibili.com/",
                   "user-agent": "Mozilla/5.0"}
        dict_data = {"bubble": bulletchat.bubble,
                     "msg": bulletchat.msg,
                     "color": bulletchat.color,
                     "mode": bulletchat.mode,
                     "fontsize": bulletchat.fontsize,
                     "rnd": str(int(time.time())),
                     "roomid": self.__roomid,
                     "csrf": cookies.bili_jct,
                     "csrf_token": cookies.bili_jct}
        dict_cookies = {"SESSDATA": cookies.sessdata,
                        "buvid3": cookies.buvid3,
                        "bili_jct": cookies.bili_jct}
        try:
            response = await aiorequest.request(method=method, url=url, data=dict_data, headers=headers,
                                                cookies=dict_cookies)
            code = response.get("code")
            if code != 0:
                raise Exception(response)
            return response
        except Exception as e:
            print(e)
