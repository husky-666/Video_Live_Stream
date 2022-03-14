"""
send_check
检查send进程运行状态，卡住则杀死重开
"""
import utils.file_io as file_io
import utils.cmd_execute as cmd_execute
import time


if __name__ == '__main__':
    while True:
        path_log = file_io.json_load(path="../data/configure.json")["cmd_send"]["logfile"]
        result = cmd_execute.run_until_complete(cmd="wc -c " + path_log)[0].strip("\n")
        time.sleep(3)
        result_later = cmd_execute.run_until_complete(cmd="wc -c " + path_log)[0].strip("\n")
        file_io.text_write(path=path_log, text="")
        if result == result_later:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " ckeck ERROR")
            cmd_execute.kills_load_file(path="../data/PID_send")
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " ckeck OK")
