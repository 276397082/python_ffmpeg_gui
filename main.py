import ast
import asyncio
import concurrent.futures
import ctypes
import logging
import os
import queue
import re
import select
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import urllib.parse
from queue import Queue
from threading import Thread
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *

import win32api
import win32process
import windnd
from tkinterdnd2 import *
from tkinterdnd2 import DND_FILES, TkinterDnD

from progress import Progress

# 配置日志格式，包括时间戳
logging.basicConfig(
    filename="./my.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", encoding="utf-8"
)  # 设置日志级别  # 日志格式  # 时间戳格式
logging.info("程序启动")


class ProgressApp:

    def __init__(self, root):
        self.root = root
        self.root.title("视频压缩")
        width = 620
        height = 720
        self.elapsed_time = 0
        self.running = False
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        self.root.geometry = "%dx%d+%d+%d" % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.minsize(width=width, height=height)
        # 创建标签和Listbox用于显示文件和目录路径
        self.label0 = tk.Label(self.root, text="拖入文件或目录")
        self.label0.place(relx=0.3816, rely=0.0306, relwidth=0.2335, relheight=0.0417)
        self.listbox = tk.Listbox(self.root)
        self.listbox.place(relx=0.0322, rely=0.0848, relwidth=0.9324, relheight=0.52)
        #
        self.files = Label(root, text="当前处理：", anchor="center")
        self.files.place(relx=0.0322, rely=0.61, relwidth=0.1272, relheight=0.0417)
        #
        self.files = Label(root, text="", anchor="center")
        self.files.place(relx=0.1707, rely=0.61, relwidth=0.6361, relheight=0.0417)
        #
        self.sav_lab = tk.Label(self.root, text="保存路径：", padx=10, pady=10)
        self.sav_lab.place(relx=0.0322, rely=0.65, relwidth=0.1272, relheight=0.0417)
        #
        self.sav_text = tk.Label(self.root, anchor="w", bg="white", text="默认为源文件路径")
        self.sav_text.place(relx=0.1820, rely=0.65, relwidth=0.5507, relheight=0.0417)
        #
        self.sav_btn = tk.Button(root, text="选择文件夹", takefocus=False, command=self.sav_btn_com)
        self.sav_btn.place(relx=0.7746, rely=0.65, relwidth=0.1884, relheight=0.0417)
        #
        # 滑块
        self.labelsp = Label(root, text="速度(0最慢)：", anchor="center")
        self.labelsp.place(relx=0.0338, rely=0.7065, relwidth=0.1256, relheight=0.0417)
        #
        self.scale_sp = tk.Scale(root, orient=HORIZONTAL, from_=0, to=10, tickinterval=1, showvalue=False)
        self.scale_sp.place(relx=0.175, rely=0.7135, relwidth=0.5597, relheight=0.5417)
        self.scale_sp.set(2)
        #
        # 时间显示
        self.timelab = Label(self.root, text="00:00:00", anchor="center")
        self.timelab.place(relx=0.7746, rely=0.75, relwidth=0.1884, relheight=0.0417)
        #
        #

        self.Combobox_EX = ttk.Combobox(root, values=["默认格式", ".MP4", ".MPEG4", ".AVI", ".WMV", ".FLV", ".MKV", ".GIF", ".WEBM", ".OGG", ".MOV"])
        self.Combobox_EX.set("默认格式")
        self.Combobox_EX.place(relx=0.7746, rely=0.7, relwidth=0.1884, relheight=0.0417)

        # 清空按钮
        self.cls_btn = tk.Button(root, text="清空", takefocus=False, command=self.cls_ui)
        self.cls_btn.place(relx=0.2559, rely=0.7816, relwidth=0.1256, relheight=0.0417)
        self.button = tk.Button(self.root, text="压缩", command=self.button_clicked)
        self.button.place(relx=0.4272, rely=0.7816, relwidth=0.1256, relheight=0.0417)
        #
        self.v1 = tk.IntVar()
        self.del_chk = tk.Checkbutton(root, text="删除源文件", variable=self.v1)
        self.del_chk.place(relx=0.60, rely=0.7816, relwidth=0.1465, relheight=0.0417)
        # self.del_chk.selection_clear()
        #
        # 当前进度：显示size
        self.sizp_lab = Label(root, text="", anchor="center")
        self.sizp_lab.place(relx=0.1771, rely=0.83, relwidth=0.6232, relheight=0.0417)
        #

        self.pr_lab = tk.Label(self.root, height=5)
        self.pr_lab.config(text="当前进度：", padx=10, pady=10)
        self.pr_lab.place(relx=0.0338, rely=0.8804, relwidth=0.1143, relheight=0.0417)

        #
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=450, mode="determinate")
        self.progress_bar.place(relx=0.1707, rely=0.8804, relwidth=0.6361, relheight=0.0417)

        #
        self.pr_lab_s = tk.Label(self.root, text="", height=5, width=60)
        self.pr_lab_s.place(relx=0.8261, rely=0.8804, relwidth=0.1304, relheight=0.0417)

        #
        self.pr_lab_full = Label(
            root,
            text="整体进度：",
            anchor="center",
        )
        self.pr_lab_full.place(relx=0.0338, rely=0.9346, relwidth=0.1143, relheight=0.0417)

        self.progressbar_full = ttk.Progressbar(self.root, length=450, orient="horizontal", mode="determinate")
        self.progressbar_full.place(relx=0.1707, rely=0.9346, relwidth=0.6361, relheight=0.0417)
        self.pr_lab_full_s = Label(
            root,
            text="",
            anchor="center",
        )
        self.pr_lab_full_s.place(relx=0.8261, rely=0.9332, relwidth=0.1304, relheight=0.0417)

        # 绑定拖放事件
        # self.root.drop_target_register(DND_FILES)
        # self.root.dnd_bind("<<Drop>>", self.on_dropB)

        windnd.hook_dropfiles(self.root, func=self.on_dropA)

        # 注册文件拖拽事件
        # windnd.hook_dropfiles(root, func=self.on_drop_callback)
        # drop_thread = threading.Thread(target=self.handle_drop, args=(self.file_queue,))
        # drop_thread.start()
        self.j = 0
        # 存储子进程的句柄
        # 捕获关闭事件
        self.process = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.thread_event = threading.Event()

    def update_time(self):
        if self.running:
            self.elapsed_time += 0.1  # 每100毫秒增加0.1秒
            hours, remainder = divmod(int(self.elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.timelab.config(text=formatted_time)  # 更新标签文本
            self.root.after(100, self.update_time)  # 每100毫秒调用一次自身以更新显示

    def start_timer(self):
        self.elapsed_time = 0

        if not self.running:
            self.running = True  # 设置为运行状态
            self.update_time()  # 开始更新时间

    def stop_timer(self):
        if self.running:
            self.running = False  # 停止计时

    def on_closing(self):
        # 处理关闭事件，杀死相关进程
        if self.process is not None:
            try:
                self.process.terminate()  # 尝试优雅地终止进程
                if os.name == "nt":  # 如果是在 Windows 系统上
                    os.kill(self.process.pid, signal.SIGTERM)
            except Exception as e:
                logging.info(f"杀死进程时出错: {e}")

        # 销毁 Tkinter 窗口
        self.root.destroy()

    def on_dropB(self, event):
        file_list = event.data.split("\n")  # 将包含多个文件路径的字符串分割成列表
        print(file_list)

    def on_dropA(self, event):
        # 获取拖拽进入窗口的文件路径
        # 创建线程来处理拖放事件
        # 清空Listbox
        self.listbox.delete(0, tk.END)
        # files = "".join((item.decode("gbk") for item in event))
        files = list((item.decode("gbk") for item in event))

        for path in files:

            self.listbox.insert(tk.END, path)
        # self.listbox.insert(END, files)

        # # 解析拖放数据
        # data = event.data
        # # 将数据按行分割，去除空白行
        # encoded_paths = [line.strip() for line in data.split(" ") if line.strip()]

        # # 解码并清理路径
        # paths = []
        # for encoded_path in encoded_paths:
        #     # 去除大括号
        #     path = encoded_path.strip("{}")

        #     # 解码十六进制转义序列
        #     path = self.decode_hex_escapes(path)

        #     # 尝试解码混合编码的字符串
        #     path = self.decode_mixed_encoding(path)

        #     paths.append(path)
        # # 插入新路径到Listbox
        # for path in paths:
        #     self.listbox.insert(tk.END, path)

    def sav_btn_com(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.sav_text.config(text="")
            self.sav_text.config(text=folder_path)

    def start_process(self, command, del_file):
        progress1 = Progress(value=self.progress_bar)  # Initialize with appropriate values
        run_command_t = threading.Thread(target=self.run_command, args=(command, del_file))
        run_command_t.daemon = True
        run_command_t.start()

    def get_file_info(self, file_path):
        # 获取文件名不含后缀
        file_name = os.path.basename(file_path)
        name, extension = os.path.splitext(file_name)

        # 获取文件所在的文件夹
        folder_name = os.path.dirname(file_path)

        return {"file_name": name, "folder_name": folder_name, "extension": extension}

    def run_command(self, command, del_file):

        try:
            logging.info("run_command 执行")

            progress2 = Progress(value=self.progress_bar)
            # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="latin-1")

            logging.info(command)
            # print(process.stdout)
            # 读取
            # for line in process.stdout:

            #     progress2.show_progress(line.strip(), self)
            #     # print(line.strip())

            # thread_pr = threading.Thread(target=self.red_process, args=(progress2, process))
            # thread_pr.daemon = True
            # thread_pr.start()

            self.red_process(progress2, process)

            exit_code = process.wait()
            if exit_code:
                progress2.clear()
                if not progress2.verbose:
                    # print(f"Error occurred with exit code {exit_code}")
                    logging.error(f"run_command: {exit_code}")
                    return False
            else:
                _del_chk = self.v1.get()
                if _del_chk:
                    os.unlink(del_file)
                self.j += 1
                self.aaa.update_progress(self.j)

        except Exception as e:
            logging.error(f"run_command_except Exception as e: {del_file}{e}")

        finally:
            progress2.cleanup()

    def run_command2(self, command, del_file):
        try:
            logging.info("run_command 执行")

            # 创建并启动子进程
            progress2 = Progress(value=self.progress_bar)  # Assuming Progress is defined elsewhere

            self.files.config(text=del_file)
            with open("./temp.txt", "w", encoding="utf-8") as temp_output:
                process = subprocess.Popen(command, stdout=temp_output, stderr=subprocess.STDOUT, encoding="uft-8")

            while True:
                time.sleep(0.5)
                thread = threading.Thread(target=self.red_txt, args=(progress2, process))
                thread.daemon = True
                thread.start()

                if process.poll() is not None:  # 进程已结束
                    break

            # time.sleep(0.1)  # 适当延迟以避免高 CPU 占用
            exit_code = process.wait()  # 等待子进程完成
            if exit_code:
                progress2.clear()
                if not progress2.verbose:
                    # print(f"Error occurred with exit code {exit_code}")
                    logging.error(f"run_command: {exit_code}")
                    return False
            else:
                _del_chk = self.v1.get()
                if _del_chk:
                    os.unlink(del_file)
                self.j += 1
                self.aaa.update_progress(self.j)
                os.remove("./temp.txt")

            logging.info(f"Process exited with code {exit_code}")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def red_txt(self, progress2, process):
        # 每次读取临时文件的新内容
        with open("./temp.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()  # 读取所有行
            if lines:  # 如果有新行
                for output in lines:

                    progress2.show_progress(output.strip(), self)  # 更新进度显示方法

    def red_process(self, progress2, process):

        for line in process.stdout:

            progress2.show_progress(line.strip(), self)

    def get_path(self):
        self.start_timer()
        # 获取滑块值
        _preset = self._preset(int(self.scale_sp.get()))

        num_items = self.listbox.size()
        sp = self.scale_sp.get()
        files_counts = self.get_files_counts()
        # 整体进度
        self.aaa = pr_main(self, self.progressbar_full, self.pr_lab_full_s, files_counts)
        self.aaa.start_progress()
        sav_lab = self.sav_text.cget("text")
        # 遍历每一个条目
        for i in range(num_items):
            item = self.listbox.get(i)
            # print(f"Item {i}: {item}")
            if os.path.isdir(item):

                self.dir_obj(item, self.j, _preset)
            else:

                # file_info = self.get_file_info(item)
                # f_name = file_info["file_name"]
                # f_fold = file_info["folder_name"]
                # f_ex = file_info["extension"]
                if os.path.exists(sav_lab):
                    sav_path = sav_lab
                else:
                    sav_path = None
                # sav_path = os.path.join(sav_lab, f_name + "_lz" + f_ex)
                if not self.is_video(item):
                    self.j += 1
                    continue
                    # drop_thread = threading.Thread(target=self.c_cmd, args=(item, full_sav_path, _preset))
                    # drop_thread.daemon = True
                    # drop_thread.start()

                aaa = self.c_cmd(item, sav_path, _preset)
                # print(aaa)
                # print(isok)
                # j = j + 1
                # self.aaa.update_progress(j)

        if self.j == files_counts:
            self.stop_timer()
            messagebox.showinfo("Title", "转换完成！")
        else:
            self.stop_timer()

        self.lock_ui(1)
        self.cls_ui()

    def get_files_counts(self):
        c = 0
        num_items = self.listbox.size()
        c += num_items
        for i in range(num_items):
            item = self.listbox.get(i)
            if os.path.isdir(item):
                file_list = os.listdir(item)
                c += len(file_list) - 1
        return c

    def dir_obj(self, path_str, j, _preset):
        folder_name = os.path.basename(path_str)
        sav_lab = self.sav_text.cget("text")
        if not os.path.exists(sav_lab):
            sav_path = path_str
        else:
            sav_path = os.path.join(sav_lab, folder_name)
        if not os.path.exists(sav_path):
            os.makedirs(sav_path)
        file_list = os.listdir(path_str)
        for files in file_list:
            files_path = os.path.join(path_str, files)
            if not self.is_video(files_path):
                self.j += 1
                continue

            # # f_name=os.path.basename(files)
            # file_info = self.get_file_info(files_path)
            # f_name = file_info["file_name"]
            # f_fold = file_info["folder_name"]
            # f_ex = file_info["extension"]

            # full_sav_path = os.path.join(sav_path, f_name + "_lz" + f_ex)

            self.c_cmd(files_path, sav_path, _preset)
            # j = j + 1
            # self.aaa.update_progress(j)

    def c_cmd(self, files, sav_path, _preset="veryfast"):

        file_info = self.get_file_info(files)
        f_name = file_info["file_name"]
        f_fold = sav_path
        f_ex = self.Combobox_EX.get()
        if f_ex == "默认格式":
            f_ex = file_info["extension"]

        self.files.config(text=f_name)
        if not sav_path:
            f_fold = file_info["folder_name"]

        sav_filepath = os.path.join(f_fold, f_name + "_lz" + f_ex)

        compress2 = '"./tools/ffmpeg.exe" -y -i "{}" -r 10 -pix_fmt yuv420p -vcodec libx264 -preset {} -profile:v baseline -crf 23 -acodec aac -b:a 32k -strict -5 "{}"'.format(
            files, _preset, sav_filepath
        )
        # print(compress2)
        # return
        # compress2 = '"./tools/ffmpeg.exe" -y -i "{}" -r 10 -pix_fmt yuv420p -vcodec libx264 -preset {} -profile baseline -crf 23 -acodec aac -b 32k -strict -5 "{}"'.format(            files, _preset, sav_filepath        )

        compress2 = shlex.split(compress2)
        # compress2 = compress2.split(" ")
        # print(compress2)
        # drop_thread = threading.Thread(target=self.run_command, args=(compress2, files))
        # drop_thread.daemon = True
        # drop_thread.start()
        # 启动多个线程

        return self.run_command(compress2, files)

    def button_clicked(self):
        if not self.listbox.size():
            messagebox.showinfo("提示", "请选择文件！")
            return
        # if not self.sav_text.cget("text"):
        #     messagebox.showinfo("提示", "保存路径为空，默认为源文件路径")
        # return
        file_path = os.path.join(os.getcwd(), "tools", "ffmpeg.exe")
        if not os.path.exists(file_path):
            messagebox.showinfo("提示", "ffmpeg不存，请将ffmpeg复制到程序的tools目录中")
            return
        # 按钮点击事件处理函数

        self.lock_ui()

        # self.get_path()
        thread = threading.Thread(target=self.get_path)
        thread.daemon = True
        thread.start()

    def cls_ui(self):
        self.listbox.delete(0, tk.END)
        self.sav_text.config(text="默认为源文件路径")
        self.v1 = tk.IntVar(value=0)
        self.del_chk.config(variable=self.v1)
        self.scale_sp.set(2)
        self.sizp_lab.config(text="")
        self.progress_bar["value"] = 0
        self.pr_lab_s.config(text="")

        self.progressbar_full["value"] = 0
        self.pr_lab_full_s.config(text="")
        self.files.config(text="")
        self.Combobox_EX.set("默认格式")

    def lock_ui(self, l=0):
        self.j = 0
        s = "disabled"
        if l != 0:
            s = "normal"

        self.listbox.config(state=s)
        self.sav_text.config(state=s)
        self.sav_btn.config(state=s)
        self.del_chk.config(state=s)
        self.scale_sp.config(state=s)
        self.cls_btn.config(state=s)
        self.button.config(state=s)
        self.sizp_lab.config(state=s)
        self.pr_lab_s.config(state=s)
        self.pr_lab_full_s.config(state=s)
        self.Combobox_EX.config(state=s)

    def decode_hex_escapes(self, s):
        # 正则表达式匹配十六进制转义序列
        hex_pattern = r"\\x([0-9A-Fa-f]{2})"
        # 使用正则表达式替换所有匹配的十六进制转义序列
        return re.sub(hex_pattern, lambda match: chr(int(match.group(1), 16)), s)

    def decode_mixed_encoding(self, s):
        # 尝试使用不同的编码解码字符串
        encodings = ["utf-8", "iso-8859-1", "gbk", "shift-jis"]
        for encoding in encodings:
            try:
                return s.encode("utf-8").decode(encoding)
            except UnicodeDecodeError:
                continue
        return s  # 如果所有编码都失败，返回原始字符串

    # 当文件或目录被拖放到窗口时调用的函数

    def is_video(self, filename):
        videoSuffixSet = {"WMV", "ASF", "ASX", "RM", "RMVB", "MP4", "3GP", "MOV", "M4V", "AVI", "DAT", "MKV", "FIV", "VOB"}
        suffix = filename.rsplit(".", 1)[-1].upper()
        if suffix in videoSuffixSet:
            return True
        else:
            return False

    def _preset(self, v: int):
        options = {
            0: "ultrafast",
            1: "superfast",
            2: "veryfast",
            3: "faster",
            4: "fast",
            5: "medium",
            6: "slow",
            7: "slower",
            8: "veryslow",
            9: "placebo",
        }
        return options[v]


class pr_main:
    def __init__(self, app, pr, lab, max):
        self.app = app
        self.pr = pr
        self.lab = lab
        self.v = self.pr["maximum"] = max

    def start_progress(self):
        self.lab.config(text=f"0% [{self.v}/{self.v}]")
        self.app.root.update_idletasks()
        # self.run_progress()
        # t1 = threading.Thread(target=self.run_progress)
        # t1.daemon = True
        # t1.start()

    def run_progress(self):

        for i in range(self.v):

            self.update_progress(i + 1)

    def update_progress(self, value):
        time.sleep(0.1)
        self.pr["value"] = value
        self.lab.config(text=f"{value/self.v*100:.0f}% [{value}/{self.v}]")

        self.app.root.update_idletasks()


if __name__ == "__main__":

    root = TkinterDnD.Tk()

    app = ProgressApp(root)

    root.mainloop()
