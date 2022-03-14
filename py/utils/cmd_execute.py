"""
utils.cmd_execute
执行shell命令以及杀死进程的操作
"""
import subprocess
import os
import psutil
from . import file_io as file_io
from typing import Tuple


def run_until_complete(cmd: str, timeout: int = None) -> Tuple[str, str]:
    """
    执行命令，等待命令执行完毕并返回结果,结果为(stdout_data, stderr_data)元组
    :param cmd: 要执行的命令
    :param timeout: 超时时间
    :return: Tuple[str, str]
    """
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            encoding="utf-8")
    try:
        outs, errs = proc.communicate(timeout=timeout)
        return outs, errs
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        return outs, errs


def run_not_wait(cmd: str) -> subprocess.Popen:
    """
    执行命令，返回Popen对象(需要注意这里Popen对象的pid是启动进程的pid，杀死进程可能还需要把子进程杀死)
    :param cmd: 要执行的命令
    :return: subprocess.Popen
    """
    proc = subprocess.Popen(cmd, shell=True)
    return proc


def wait_id(pid: int) -> None:
    """
    等待pid进程执行完毕
    :param pid: 进程pid
    :return: None
    """
    try:
        os.waitid(os.P_PID, pid, os.WEXITED)
    except Exception as exc:
        print(exc)


def wait(popen: subprocess.Popen) -> None:
    """
    等待popen对象生成的进程执行完毕
    :param popen: subprocess.Popen
    :return: None
    """
    try:
        popen.wait()
    except Exception as exc:
        print(exc)


def kills(pid: int) -> None:
    """
    杀死pid进程的子进程(不含该pid进程)
    :param pid: 进程pid
    :return: None
    """
    try:
        proc = psutil.Process(pid)
        while len(proc.children()) > 0:
            proc.children()[0].kill()
        print("killed....")
    except Exception as exc:
        print(exc)


def kills_old_method(pid: int) -> None:
    """
    杀死pid进程及其子进程
    :param pid: 进程pid
    :return: None
    """
    cmd = "ps -ef | awk '{print $2\" \"$3}'| grep " \
          + str(pid) + " | awk '{print $1}'"
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            encoding="utf-8")
    str_pid = proc.communicate()[0].replace("\n", " ")
    subprocess.Popen("kill -9 " + str_pid, shell=True)


def kills_load_file(path: str) -> None:
    """
    读取路径为path的文件，提取pid并杀死pid进程的子进程
    :param path: 文件路径
    :return: None
    """
    try:
        read = file_io.text_read(path=path)
        for line in read:
            for num_str in line.split():
                if num_str.isdigit():
                    kills(pid=int(num_str))
    except FileNotFoundError as exc:
        print(exc)
