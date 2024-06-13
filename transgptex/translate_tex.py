"""\
翻译单个tex文件

Usage: 翻译单个tex文件
"""

from .latex_spilter import LatexTextSplitter
from .llm_api_async import Translator
from .preprocess_tex import preprocess_tex_content
from .config import config
import os
import re

def translate_single_tex(tex_file_path: str, output_path: str, language_to: str):
    # 指示翻译中
    print(f"正在翻译 {os.path.basename(tex_file_path)} ...")

    # 读取tex文件
    with open(tex_file_path, "r", encoding="utf-8") as f:
        tex_text = f.read()
    
    # 进行预处理
    tex_text, holder_index_to_content = preprocess_tex_content(tex_text)

    # 切分器，注意参数设置
    ls = LatexTextSplitter(chunk_size=config.chunk_size)
    tex_texts = ls.split_text(tex_text)

    # 实例化翻译器
    translator = Translator()

    combined_texts = translator.translate_batch(tex_texts, language_to)

    translated_tex = "\n".join(combined_texts)

    # 后处理，把占位符还原
    postprocess_tex = ""
    for line in translated_tex.split("\n"):
        if line.startswith("ls_replace_holder_"):
            holder_index = line.replace("ls_replace_holder_", "")
            if holder_index.isdigit() and int(holder_index) >= 0 and int(holder_index) < len(holder_index_to_content):
                holder_index = int(holder_index)
                holder_content = holder_index_to_content[holder_index]
                postprocess_tex += "\n" + holder_content
            else:
                print(f"{line} 疑似占位符但未解析成功...")
                postprocess_tex += "\n" + line
        elif line.startswith("====="):
            # 可能是标识符被llm翻译进去了，忽略即可
            continue
        else:
            postprocess_tex += "\n" + line

    # 写入文件
    with open(os.path.join(output_path, os.path.basename(tex_file_path)), "w", encoding="utf-8") as f:
        f.write(postprocess_tex)

    print(f" {os.path.basename(tex_file_path)} 翻译完成!")