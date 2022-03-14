"""
change
识别命令后执行切换操作
"""
import sys
import re
import utils.file_io as file_io
import utils.cmd_execute as cmd_execute
import utils.play_enum as play_enum


if __name__ == '__main__':
    # 只处理sys.argv[1]
    if len(sys.argv) == 2:
        arg = sys.argv[1]

        # 换碟：本集结束播放
        if re.match(r'^@ *换碟 *$', arg) is not None:
            cmd_execute.kills_load_file(path="../data/PID_push")
            # 刷新
        if re.match(r'^@ *刷新 *$', arg) is not None:
            cmd_execute.kills_load_file(path="../data/PID_send")
        # 马上重播本集
        if re.match(r'^@ *[Rr] *$', arg) is not None:
            file_io.text_write(path="../data/play_skip", text="R 1")
            cmd_execute.kills_load_file(path="../data/PID_push")
        # 选集播放
        if re.match(r'^@ *([1-9]\d*) *$', arg) is not None:
            memory = str(int(re.match(r'^@ *([1-9]\d*) *$', arg).group(1)) - 1)
            file_io.text_write(path="../data/loop_tag", text=str(play_enum.ListLoopState.LOOP_BREAK.value))
            file_io.text_write(path="../playlist/playlist_memory.txt", text=memory)
            cmd_execute.kills_load_file(path="../data/PID_push")

        # 匹配跳集指令
        match_result = re.match(r'^@ *([NnPp]) *([1-9]\d*) *$', arg)
        if match_result is not None:
            file_io.text_write(path="../data/play_skip",
                               text=match_result.group(1).upper() + " " + match_result.group(2))
            cmd_execute.kills_load_file(path="../data/PID_push")
        else:
            # 匹配切换模式指令
            match_result = re.match(r'^@@ *([NnPpRr]) *$', arg)
            if match_result is not None:
                file_io.text_write(path="../data/play_method", text=match_result.group(1).upper())
            else:
                # 匹配换剧指令
                match_result = re.match(r'^@# *换剧 *([^ ]*) *$', arg)
                if match_result is not None:
                    try:
                        lines = file_io.text_read(path="../playlist/" + match_result.group(1))
                        file_io.text_write(path="../playlist/playlist.txt", text="".join(lines))
                        file_io.text_write(path="../data/loop_tag", text=str(play_enum.ListLoopState.LOOP_BREAK.value))
                        file_io.text_write(path="../playlist/playlist_memory.txt", text="")
                        cmd_execute.kills_load_file(path="../data/PID_push")
                    except FileNotFoundError as exc:
                        print(exc)
