"""
stop_pipe
停止维持推流管道的开启
"""
import utils.cmd_execute as cmd_execute


if __name__ == '__main__':
    cmd_execute.kills_load_file(path="../data/PID_keep_pipe")
