# coding:utf-8

import gradio as gr

from pylibs import log_api
import logging
import os
from pylibs import config

def hello(name):
    return "Hello " + name + "!"

if __name__ == '__main__':
    # 初始化日志
    log_path_dir = os.path.join(os.path.expanduser('~'), 'bear_video_log')
    if os.path.exists(log_path_dir) == False:
        os.mkdir(log_path_dir)
    log_file_path = os.path.join(log_path_dir, "run")
    log_api.init_logger(level="INFO", issave=True, filename=log_file_path, filenum=10, filesize=50)

    # 初始化配置
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    config.init(config_path)
    logging.info(f'Config path: {config_path}')
    logging.info(f'Config mode size: {config.get("ModeSize", default="base")}')

    # 初始化webui
    with gr.Blocks() as app:
        gr.Markdown('''# 阿熊视频工具箱
                    ### 字幕提取 & 翻译''')
        audiofile = gr.File(file_types=['.mp3', '*.wav', '*.aac', '*.flac', '*.ogg', '*.m4a'], label="上传音频文件")

        app.launch()