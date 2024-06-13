"""\
挑出Latex项目中值得翻译的文件，并且将不需要翻译的文件复制到输出路径中

Usage: 挑出Latex项目中值得翻译的文件，并调用translate_tex进行翻译。
"""

from .translate_tex import translate_single_tex
import os
import shutil


def select_file(input_dir: str, output_dir: str, language_to: str):
    # 将tex文件进行翻译，其他文件直接复制
    # 如果有文件夹的情况，则需要递归处理
    # 先新建输出路径
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        # 组合成真实路径
        abs_path = os.path.join(input_dir, file)

        if os.path.isdir(abs_path):
            # 是文件夹直接递归处理
            select_file(abs_path, os.path.join(output_dir, file), language_to)
        else:
            # 这里是文件
            if file.endswith(".tex"):
                translate_single_tex(abs_path, output_dir, language_to)
            else:
                # 直接复制过去
                shutil.copyfile(abs_path, os.path.join(output_dir, file))


