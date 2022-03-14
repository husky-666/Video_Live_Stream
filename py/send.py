"""
send
读取管道中的数据，推送至rtmp服务器
"""
import utils.file_io as file_io
import utils.cmd_execute as cmd_execute
import time
from atexit import register


if __name__ == '__main__':
    @register
    def __clean_cmd():
        cmd_execute.kills_load_file(path="../data/PID_send")
        print("--------------------run __clean_cmd--------------------")


    while True:
        # 获取ffmpeg运行参数
        configure_send = file_io.json_load(path="../data/configure.json")["cmd_send"]
        arg_pipe_output = configure_send["pipe_output"]
        arg_rtmp_address = configure_send["rtmp_address"]
        arg_logfile = configure_send["logfile"]
        # 组合命令
        cmd_send = "ffmpeg -hide_banner -re -i " + arg_pipe_output \
                   + " -vcodec copy -acodec copy -f flv " + "\"" + arg_rtmp_address + "\""\
                   + " 2>&1 | tee -a " + arg_logfile
        # 运行命令，返回popen对象
        process_send = cmd_execute.run_not_wait(cmd=cmd_send)
        # 把send_pid保存到文件
        file_io.text_write(path="../data/PID_send", text=str(process_send.pid))
        # 等待进程执行完毕
        cmd_execute.wait(popen=process_send)
        # 以免命令错误时循环过于频繁消耗资源
        time.sleep(1)
