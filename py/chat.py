import time
import asyncio
import queue
import copy
from bilibili_live import live
from utils import cmd_execute


# 直播间房间id
roomid = 直播间号
# RoomCollection类，用于连接直播间
room = live.RoomCollection(roomid=roomid)
# RoomOperation类，用于发送弹幕
room_operation = live.RoomOperation(roomid=roomid)
# 弹幕类，用于设置弹幕信息
bulletchat = live.BulletChat(msg="")
# Cookies类，身份认证
cookies = live.Cookies(sessdata="",
                       buvid3="",
                       bili_jct="")
# 队列，存在待发送的弹幕信息
queue_chat = queue.Queue()
# 字典，存放收到的礼物信息，传输到队列后数据消失
dict_gift = {}
# 用于标记dict_gift是否有新添加的信息
change_tag = False


# 把礼物信息存放到dict_gift中
async def add_gift_to_dict(user_name: str, gift_name: str, gift_num: str, gift: dict):
    if user_name not in gift:
        gift.setdefault(user_name, {})
    num = gift[user_name].setdefault(gift_name, 0)
    gift[user_name][gift_name] = int(gift_num) + num
    global change_tag
    change_tag = True


# 把dict_gift中的礼物信息提取并放到queue_chat中，清空dict_gift
async def add_dict_to_queue(gift: dict, queue_chat: queue.Queue):
    while True:
        if len(gift) > 0:
            global change_tag
            change_tag = False
            await asyncio.sleep(2)
            # tag为True，说明有新的礼物存放到dict_gift，继续等待
            if change_tag:
                continue
            dict_copy = copy.deepcopy(gift)
            gift.clear()
            # 提取礼物信息放入队列
            for name in dict_copy:
                for gift_name in dict_copy[name]:
                    count = dict_copy[name][gift_name]
                    queue_chat.put('[自动回复]感谢 ' + name + ' 赠送了' + str(count) + '个' + gift_name)
            dict_copy.clear()

        await asyncio.sleep(5)


# 从queue_chat队列提取信息后，发送到直播间
async def send_msg_to_room(queue_chat: queue.Queue, bulletchat: live.BulletChat, cookies: live.Cookies):
    while True:
        while not queue_chat.empty():
            bulletchat.msg = queue_chat.get()
            try:
                await room_operation.send_bulletchat(bulletchat=bulletchat, cookies=cookies)
            except Exception as exc:
                print(exc)
            await asyncio.sleep(7)
        else:
            await asyncio.sleep(5)


@room.on("DANMU_MSG")
async def on_danmu(msg):
    uname = msg['info'][2][1]
    text = msg['info'][1]
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['info'][9]['ts']))
    print('[danmu]' + 'time:' + localtime + ' ' + uname + ':' + text)
    if text[:1] == "@":
        cmd_execute.run_until_complete(cmd="python3 change.py " + "\"" + text + "\"")


@room.on("SEND_GIFT")
async def on_gift(msg):
    uname = msg['data']['uname']
    gift_num = str(msg['data']['num'])
    act = msg['data']['action']
    gift_name = msg['data']['giftName']
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['data']['timestamp']))
    print('[gift]' + 'time:' + localtime + ' ' + uname + ' ' + act + ' ' + gift_num + ' ' + gift_name)
    global dict_gift
    # 使用字典存放礼物信息
    await add_gift_to_dict(user_name=uname, gift_name=gift_name, gift_num=gift_num, gift=dict_gift)


@room.on("COMBO_SEND")
async def on_gifts(msg):
    uname = msg['data']['uname']
    gift_num = str(msg['data']['combo_num'])
    act = msg['data']['action']
    gift_name = msg['data']['gift_name']
    print('[combo_gift]' + uname + ' ' + act + ' ' + gift_num + ' ' + gift_name)


@room.on("INTERACT_WORD")
async def on_welcome(msg):
    global queue_chat
    uname = msg['data']['uname']
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['data']['timestamp']))
    if msg['data']['msg_type'] == 2:
        print('[people]' + 'time:' + localtime + ' ' + uname + ' ' + '关注了直播间')
        queue_chat.put('[自动回复]感谢 ' + uname + '关注直播间^.^')
    else:
        print('[people]' + 'time:' + localtime + ' ' + uname + ' ' + '进入直播间')


@room.on("ENTRY_EFFECT")
async def on_welcome_2(msg):
    uname = msg['data']['copy_writing'].split('<%')[1].split('%>')[0]
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['data']['trigger_time'] / 1000000000))
    print('[people]高能榜' + 'time:' + localtime + ' ' + uname + ' ' + '进入直播间')


async def main():
    while True:
        remote = 'wss://broadcastlv.chat.bilibili.com:443/sub'
        task_dict_to_queue = asyncio.create_task(add_dict_to_queue(gift=dict_gift, queue_chat=queue_chat))
        task_msg = asyncio.create_task(send_msg_to_room(queue_chat=queue_chat, bulletchat=bulletchat, cookies=cookies))
        task_room_connect = asyncio.create_task(room.startup(uri=remote))
        try:
            await asyncio.gather(task_dict_to_queue, task_msg, task_room_connect)
        except Exception as exc:
            print(exc)
            task_dict_to_queue.cancel()
            task_msg.cancel()
            task_room_connect.cancel()


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except Exception as exc:
        print("Error:", exc)
