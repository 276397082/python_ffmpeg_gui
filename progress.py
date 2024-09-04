""" Author Aniesh A.V. """

#  import sys
import logging
import threading
import time
import tkinter as tk

from tqdm import tqdm

from stdout_analyser import StdoutAnalyzer

# 配置日志格式，包括时间戳
logging.basicConfig(
    filename="./my.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", encoding="utf-8"
)  # 设置日志级别  # 日志格式  # 时间戳格式


class Progress:
    """Shows progress of the encoding task.
    Stdout of ffmpeg must be fed into this class
    line by line."""

    def __init__(self, value):
        self.analyzer = StdoutAnalyzer()
        self.percent_complete = 0
        self.pbar = tqdm(total=100)
        # self.pbar = tqdm(total=100,ascii=True)
        self.verbose = False
        self.stdout_log = ""
        self.value = value

    @staticmethod
    def calculate_percent_complete(result, value):
        duration_in_seconds = result["duration"].time_in_secs
        if duration_in_seconds == 0:
            return 100
        curr_time_in_seconds = result["time"].time_in_secs
        percent_complete = int(curr_time_in_seconds * 100 / duration_in_seconds)
        if percent_complete > 100:
            percent_complete = 100

        return percent_complete

    @staticmethod
    def _estimate_total_size(curr_size, percent_complete):
        if curr_size == 0:
            return 0
        return curr_size * 100 // percent_complete

    def show_progress(self, line, value):
        """Shows a progress bar."""
        self.stdout_log += line + "\n"
        result = self.analyzer.analyze(line)
        # print(result)
        if "duration" in result and "time" in result:
            percent_complete = self.calculate_percent_complete(result, value)
            if percent_complete > self.percent_complete:

                self._update_pbar(percent_complete, result, value)

                self.percent_complete = percent_complete
        elif self.verbose:
            # print(line, flush=True)
            logging.info(line)

    def _update_pbar(self, percent_complete, result, V):
        curr_sz = result.get("size", 0) // 1024
        total_sz = self._estimate_total_size(curr_sz, percent_complete)
        fps = result.get("fps", 0)
        self.pbar.set_postfix(size="{}/{}".format(curr_sz, total_sz), fps=fps)
        # print(aaa)
        time.sleep(0.1)
        # V.text_var2.set(self.pbar.aaa[1])

        self.pbar.update(percent_complete - self.percent_complete)

        self._up_ui(percent_complete, V)
        # szize = self.pbar.aaa[1].split("||")
        # V.progress_bar["value"] = percent_complete

        # V.sizp_lab.config(text=szize[1])
        # V.pr_lab_s.config(text=szize[0])
        # time.sleep(0.1)
        # V.root.update_idletasks()

        # V.text_var1.set("{}%".format(percent_complete))
        # V.text_var2.set("{}%,size={}/{},fps={}".format(percent_complete, curr_sz, total_sz, fps))

    def _up_ui(self, percent_complete, V):
        szize = self.pbar.aaa[1].split("||")

        V.progress_bar["value"] = percent_complete

        V.sizp_lab.config(text=szize[1])
        V.pr_lab_s.config(text=szize[0])
        time.sleep(0.1)
        # V.root.update_idletasks()
        V.root.update_idletasks()

    def cleanup(self):
        self.pbar.close()

    def clear(self):
        self.pbar.clear()


if __name__ == "__main__":
    P = Progress(0)
    P.show_progress("Duration: 00:00:50.45, start: 0.000000, bitrate: 102374 kb/s", 0)

    LINE = "frame= 1285 fps= 41 q=27.0 size=    5185kB" " time=00:00:05.50 bitrate= 824.8kbits/s speed=1.64x"
    P.show_progress(LINE, 0)
