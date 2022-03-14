"""
push
推送视频至管道，读取指令调整播放计划
"""
import utils.file_io as file_io
import utils.LinkList as LinkList
import utils.cmd_execute as cmd_execute
import utils.play_enum as play_enum
import re
import time
from atexit import register


if __name__ == '__main__':
    @register
    def __clean_cmd():
        cmd_execute.kills_load_file(path="../data/PID_push")
        print("--------------------run __clean_cmd--------------------")


    # 设置循环标识
    file_io.text_write(path="../data/loop_tag", text=str(play_enum.ListLoopState.LOOP_KEEP.value))
    # 清除文件中的指令
    file_io.text_write(path="../data/play_skip", text="")
    # 设置播放模式为顺序播放
    file_io.text_write(path="../data/play_method", text=play_enum.PlayMethod.NEXT.value)
    link_list = LinkList.DoubleCircleLinkList()

    while True:
        # 清空链表
        link_list.clean()
        # 获取播放列表,存放到链表
        playlist = file_io.text_read(path="../playlist/playlist.txt")
        for line in playlist:
            if len(line.strip(" \n")) > 0 and len(line.split()) > 1:
                link_list.append(line.split()[1].strip("'\""))

        # 获取并检查播放进度
        playlist_memory = file_io.text_read(path="../playlist/playlist_memory.txt")
        if len(playlist_memory) > 0:
            playlist_memory = playlist_memory[0].strip("\n ")
            if playlist_memory.isdigit():
                playlist_memory = int(playlist_memory)
                if playlist_memory >= link_list.length():
                    playlist_memory = 0
            else:
                playlist_memory = 0
        else:
            playlist_memory = 0

        # 保存播放进度到文件
        file_io.text_write(path="../playlist/playlist_memory.txt", text=str(playlist_memory))

        # 获取记忆进度对应的节点
        Node_memory = link_list.getNode(playlist_memory)
        # 设置循环标记
        file_io.text_write(path="../data/loop_tag", text=str(play_enum.ListLoopState.LOOP_KEEP.value))

        while True:
            # 获取ffmpeg运行参数
            configure_push = file_io.json_load(path="../data/configure.json")["cmd_push"]
            arg_skip_start = configure_push["skip_start"]
            arg_skip_end = configure_push["skip_end"]
            arg_vcodec = configure_push["vcodec"]
            arg_acodec = configure_push["acodec"]
            arg_format = configure_push["format"]
            arg_pipe_input = configure_push["pipe_input"]
            # 获取视频信息，用于提取视频时长（包含单位为秒的时长以及格式为HH:MM:SS的时长）
            media_message = cmd_execute.run_until_complete(cmd='ffprobe -hide_banner -show_format '
                                                               + Node_memory.item + ' 2>&1')[0]
            # 文件存在则执行命令，不存在则跳过本次执行
            if media_message.count("No such file or directory") == 0:
                # 提取时长后，计算：结束时间 = 总时长 - 跳过片尾时长
                arg_end_time = str(int(re.search(r'duration=(.*?)\.', media_message).group(1)) - int(arg_skip_end))
                # 获取HH:MM:SS格式时间，并转换为HH\:MM\:SS
                arg_Duration = re.search(r'Duration: (.*?)\.', media_message).group(1).replace(":", r"\:")
                # 获取并设置filter_complex参数
                try:
                    arg_filter_complex = file_io.text_read(path="../data/filter_complex.txt")[0].strip("\n") \
                        .replace("$filename",
                                 Node_memory.item[Node_memory.item.rfind("/") + 1:Node_memory.item.rfind(".mp4")]) \
                        .replace("$Duration", arg_Duration) \
                        .replace("$jump_start", arg_skip_start)
                except Exception as exc:
                    arg_filter_complex = ""
                # 组合命令
                cmd_push = "ffmpeg -hide_banner -ss " + arg_skip_start + " -to " + arg_end_time + " -i " \
                           + Node_memory.item + " " + arg_vcodec + " " + arg_filter_complex \
                           + " " + arg_acodec + " " + arg_format + " | cat - >> " + arg_pipe_input
                # 运行命令，返回popen对象
                process_push = cmd_execute.run_not_wait(cmd=cmd_push)
                # 把push_pid保存到文件
                file_io.text_write(path="../data/PID_push", text=str(process_push.pid))
                # 等待进程执行完毕
                cmd_execute.wait(popen=process_push)
            else:
                print(media_message)

            # 以免命令错误时循环过于频繁消耗资源
            time.sleep(0.3)

            # 若循环指示为LOOP_BREAK,则跳出循环
            loop_tag = file_io.text_read(path="../data/loop_tag")
            if len(loop_tag) > 0 \
                    and loop_tag[0].strip("\n").isdigit() \
                    and int(loop_tag[0].strip("\n")) == play_enum.ListLoopState.LOOP_BREAK.value:
                file_io.text_write(path="../data/loop_tag", text=str(play_enum.ListLoopState.LOOP_KEEP.value))
                # 清除文件中的指令
                file_io.text_write(path="../data/play_skip", text="")
                break

            # 准备获取下一个播放节点

            tuple_play_method = (play_enum.PlayMethod.NEXT.value,
                                 play_enum.PlayMethod.PREV.value,
                                 play_enum.PlayMethod.REPEAT.value)
            # 读取指令
            play_skip = file_io.text_read(path="../data/play_skip")
            # 清除文件中的指令
            file_io.text_write(path="../data/play_skip", text="")
            # 指令存在则检查格式是否正确
            if len(play_skip) > 0 and re.match(r'^([NPR]) +([1-9]\d*)$', play_skip[0].strip("\n")) is not None:
                play_method, num = re.match(r'^([NPR]) +([1-9]\d*)$', play_skip[0].strip("\n")).groups()
                num = int(num)
            # 指令不存在或格式错误则按原来的模式继续播放
            else:
                # 获取播放模式
                play_method = file_io.text_read(path="../data/play_method")
                if len(play_method) > 0 and play_method[0].strip("\n") in tuple_play_method:
                    play_method = play_method[0].strip("\n")
                else:
                    file_io.text_write(path="../data/play_method", text=play_enum.PlayMethod.NEXT.value)
                    play_method = play_enum.PlayMethod.NEXT.value
                num = 1
            # 按对应模式处理
            if play_method == play_enum.PlayMethod.NEXT.value:
                for i in range(num):
                    Node_memory = Node_memory.next
                    playlist_memory += 1
            elif play_method == play_enum.PlayMethod.PREV.value:
                for i in range(num):
                    Node_memory = Node_memory.prev
                    playlist_memory -= 1
            elif play_method == play_enum.PlayMethod.REPEAT.value:
                pass
            # 重新计算好进度，写入文件
            playlist_memory %= link_list.length()
            file_io.text_write(path="../playlist/playlist_memory.txt", text=str(playlist_memory))
