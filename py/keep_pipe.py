"""
keep_pipe
维持推流管道的开启
"""
import utils.cmd_execute as cmd_execute
import utils.file_io as file_io


if __name__ == '__main__':
    # 若管道已维持则先取消维持
    cmd_execute.run_until_complete(cmd="python3 stop_pipe.py")
    # 管道不存在则创建管道
    cmd_execute.run_until_complete(cmd="mkfifo ../pipe/pipe_push ../pipe/keep1 ../pipe/keep2")
    # 维持管道打开
    pid_keep1 = cmd_execute.run_not_wait(cmd="cat ../pipe/keep1 > ../pipe/pipe_push").pid
    pid_keep2 = cmd_execute.run_not_wait(cmd="cat ../pipe/keep2 < ../pipe/pipe_push").pid
    # 把pid保存到文件，用于取消维持管道
    file_io.text_write(path="../data/PID_keep_pipe", text=str(pid_keep1) + " " + str(pid_keep2))
