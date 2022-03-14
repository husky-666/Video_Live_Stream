<h1>Video_Live_Stream</h1>
一个视频推流小工具

----------

<h1>简介</h1>
Video_Live_Stream是在Linux系统下基于python调用ffmpeg实现的简易推流工具，基本功能如下：

* 读取播放列表，按列表顺序循环推流视频至rtmp服务器。
* 添加了`bilibili直播间弹幕模块`，可接收及发送弹幕。
* 可通过指令修改`视频播放模式`，结合弹幕模块可以直播间操作播放模式。

<h1>文件结构</h1>
Video_Live_Stream

* data
    * configure.json
	    * <u>配置文件，存放推流参数</u>
	* filter_complex.txt
	    * <u>存放滤镜参数</u>
	* loop_tag
	    * <u>存放循环标识</u>
	* PID_keep_pipe
	    * <u>存放keep_pipe的pid</u>
	* PID_push
	    * <u>存放push进程中ffmpeg进程的pid</u>
	* PID_send
	    * <u>存放send进程中ffmpeg进程的pid</u>
	* play_method
	    * <u>存放播放模式</u>
	* play_skip
	    * <u>存放指令</u>

* font
    * msyh.ttc
	    * <u>字体文件(修改后需要在data/filter_complex.txt中同步修改)</u>
* log
    * log.log
	    * <u>send进程输出日志，结合py/send_check.py使用</u>
* pipe
    * keep1
	    * <u>管道文件，用于维持pipe/pipe_push开启</u>
	* keep2
	    * <u>管道文件，用于维持pipe/pipe_push开启</u>
	* pipe_push
	    * <u>管道文件，用于推流</u>
* playlist
    * playlist.txt
	    * <u>当前播放列表</u>
	* playlist_memory.txt
	    * <u>用于保存播放进度</u>
	* ...
	    * <u>需自行创建的播放列表</u>
	* ...
* py
    * bilibili_live
	    * aiorequest.py
		    * <u>网络请求模块</u>
	    * live.py
		    * <u>直播间连接模块</u>
	* utils
	    * cmd_execute.py
		    * <u>命令执行模块</u>
	    * file_io.py
		    * <u>文件读写模块</u>
	    * LinkList.py
		    * <u>链表模块</u>
	    * play_enum.py
		    * <u>自定义枚举模块</u>
	* change.py
		* <u>发送指令</u>
	* chat.py
		* <u>直播间连接，弹幕接收与发送</u>
	* keep_pipe.py
		* <u>维持管道</u>
	* stop_pipe.py
		* <u>取消维持管道</u>
	* push.py
		* <u>视频推流至管道</u>
	* send.py
		* <u>管道数据推流至rtmp服务器</u>
	* send_check.py
		* <u>检查send进程运作</u>
* video
    * xxx文件夹
	    * 01.mp4
		    * <u>视频名称</u>
		* 02.mp4
		* ...
		* ...
	* ...
	* ...

----------

<h1>准备工作</h1>
首先把压缩包下载到本地然后解压，做好以下准备。  

1、修改 data/configure.json中的参数。  

* cmd_push存放着push.py需要的ffmpeg命令参数，请按需修改(pipe_input一般不改)。
* cmd_send存放着send.py需要的ffmpeg命令参数，一般只需要修改rtmp_address。
* location_dir暂时没有使用，可以不管。

2、修改data/filter_complex.txt。  

* 文件中保存的使用到的滤镜配置，若不需要或者设置了-vcodec copy，则直接清空文件内容或者删除文件。

3、准备好font文件夹中的字体文件。  

* data/filter_complex.txt里直接指向使用font/msyh.ttc，若没有该文件或需要使用其它字体文件，请修改。

4、准备好视频文件及播放列表。  

* 在video文件夹里新建文件夹（例如：dir_1），在新建的文件夹中存放视频文件（需要后缀为.mp4，需要其它后缀的可在push.py中修改）。
* 在playlist文件夹中新建播放列表，指向刚刚存放的视频文件，新建的播放列表名称不含后缀（例如：playlist_1，而不是playlist_1.txt）。
* 播放列表格式请参考ffmpeg的播放列表格式(file '../video/文件夹/视频文件')，例如
    * file '../video/dir_1/01.mp4'
	* file '../video/dir_1/02.mp4'

5、python一般系统都内置了，没有的话请自行安装（还没进行版本测试，建议安装python3.8以上的版本），然后需要提前安装几个python模块，打开终端后执行。
```shell
pip3 install psutil brotli aiohttp
```

6、还可能需要使用到shell中的screen命令（建议先学习一下screen的用法）。
```shell
sudo apt install screen
```

7、最后不要忘了修改py/chat.py中的参数

* 修改roomid为你的直播间id
* 修改Cookies中的sessdata、buvid3、bili_jct
----------

<h1>使用方法</h1>
1、把待播放的视频列表内容复制到playlist/playlist.txt中  


2、进入py目录。  

在当前解压目录执行
```shell
cd ./Video_Live_Stream/py
```

3、执行以下命令。

首先执行
```shell
python3 keep_pipe.py
```

然后执行
```shell
screen -S live
```
进入窗口后，执行
```shell
python3 push.py

键盘按Ctrl+a+c

python3 send.py

键盘按Ctrl+a+c

python3 send_check.py

键盘按Ctrl+a+c

python3 chat.py

键盘按Ctrl+a+d
```


4、停止命令。

进入对应的窗口使用Ctrl+c停止命令，最后执行
```shell
python3 stop_pipe.py
```
即可

----------

<h1>指令说明</h1>
可在b站直播间发送弹幕调整播放模式。

* 换碟：本集结束播放
    * 输入：@换碟
* 刷新：重新打开send中的ffmpeg进程
    * 输入：@刷新
* 马上重播本集（大小写均可）
    * 输入：@R
* 选集播放
    * 输入：@集数，例如@12
* 跳集（大小写均可）
    * 输入：@N数量 跳到下n集（以顺序方式，不受播放模式影响）
	* 输入：@P数量 跳到上n集（以顺序方式，不受播放模式影响）
* 修改顺序模式（大小写均可）
    * 输入：@@N 顺序播放
	* 输入：@@P 逆序播放
	* 输入：@@R 重复单集播放
* 换剧
    * 输入：@#换剧+播放列表名称 ，例如@#换剧playlist_1
----------

<h1>问题反馈</h1>
这个工具主要是写来自用的，目前<a href="https://live.bilibili.com/2010774">我的b站直播间</a>在使用，有什么问题交流的话可以在b站私信我。
