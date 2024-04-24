# coding:utf-8

import gradio as gr

from pylibs import log_api
import logging
import os
from pylibs import config
from pylibs import whisper_api
import tempfile
import shutil

def save_subtitle(audio_file_path, subtitle_content):
    tmpdir = tempfile.gettempdir()
    # 获取audio_file_path的文件名,去掉后缀
    audio_file_name = os.path.basename(audio_file_path).split('.')[0]
    logging.info(f'tmpdir:{tmpdir}, audio_file_path:{audio_file_path}, audio_file_name:{audio_file_name} subtitle_content:{subtitle_content[:20]}')

    tmp_file_total_path = os.path.join(tmpdir, audio_file_name)
    # 打开复制到新路径后的文件
    with open(tmp_file_total_path,'w', encoding='utf-8') as f:
         f.write(subtitle_content)

    # 返回新文件的的地址（注意这里）
    return tmp_file_total_path


def main():
    # 初始化日志
    log_path_dir = os.path.join(os.path.expanduser('~'), 'bear_video_log')
    if os.path.exists(log_path_dir) == False:
        os.mkdir(log_path_dir)
    log_file_path = os.path.join(log_path_dir, "run")
    log_api.init_logger(level="INFO", issave=False, filename=log_file_path, filenum=10, filesize=50)
    # 初始化配置
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    config.init(config_path)
    logging.info(f'Config path: {config_path}')
    logging.info(f'Config mode size: {config.get("ModeSize", default="base")}')

def start_transcribe(audio, model_size, language, format):
    language_choice = whisper_api.get_language(language)
    logging.info(f"start to transcribe. modelsize:{model_size}, language:{language_choice}, format:{format}")
    res = whisper_api.extract_subtitles(audio, model_size=model_size, target_language=language_choice, use_gpu=False)
    
    return res[format], res 

def on_change_format(format, state):
    logging.info(f"State: {state}, Format: {format}")
    print(f"State: {state}, Format: {format}")
    if format not in state:
        return ""
    return state[format]


# 初始化webui
with gr.Blocks() as demo:
    trans_result_state = gr.State({})

    # gr.Markdown('''# 阿熊视频工具箱
    #             ### 字幕提取 & 翻译''')
    file_audio = gr.File(file_types=['.mp3', '*.wav', '*.aac', '*.flac', '*.ogg', '*.m4a'], label="上传音频文件")
    dropdown_lang = gr.Dropdown(whisper_api.get_language_choices(), value='自动检测', label="选择字幕语言")
    radio_model_size = gr.Radio(whisper_api.g_model_sizes, value='base', label="选择模型大小")
    transcribe_btn = gr.Button("提取字幕", variant="primary")

    with gr.Group():
        radio_format = gr.Radio(whisper_api.g_supported_subtitle_formats, value='srt', label="输出格式")
        output_textbox = gr.Textbox("", label="提取结果", type="text", lines=10)
        button_save = gr.Button("保存字幕", variant="primary")
        file_save = gr.File(label="保存字幕")

    transcribe_btn.click(start_transcribe, inputs=[file_audio, radio_model_size, dropdown_lang, radio_format], outputs=[output_textbox, trans_result_state])
    radio_format.change(on_change_format, inputs=[radio_format, trans_result_state], outputs=output_textbox)
    button_save.click(save_subtitle, inputs=[file_audio, output_textbox], outputs=file_save)

if __name__ == '__main__':
    main()
    demo.launch()