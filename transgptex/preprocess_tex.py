"""\
预处理tex文件，将格式进行统一以便后续进行启发式的处理。

Usage: 预处理tex文件的函数
"""

from typing import Any, List, Dict, Union
import sys
import re

def search_main_tex(tex_dict: Dict[str, str]):
    # 搜寻主tex文件，主要有几个特征点
    # 1. 存在\documentclass命令
    # 2. 存在\author命令
    # 3. 存在\usepackage命令
    # 以上三个特征每命中一个得一分，最高分的就是主tex文件
    main_tex_score = {}
    for filename, content in tex_dict.items():
        if "\\documentclass" in content:
            main_tex_score[filename] = main_tex_score.get(filename, 0) + 1
        
        if "\\author" in content:
            main_tex_score[filename] = main_tex_score.get(filename, 0) + 1

        if "\\usepackage" in content:
            main_tex_score[filename] = main_tex_score.get(filename, 0) + 1
    
    # 如果查询不到主文件就退出
    if len(main_tex_score) == 0:
        print(f"未查找到主tex文件，程序退出...")
        sys.exit(100)
    
    return max(main_tex_score, key=main_tex_score.get)


# 辅助的正则表达式
comment_pattern = re.compile(r"(?<!\\)%.*")
consecutive_line_breaks_pattern = re.compile(r"\n{3,}")
bibliography_pattern = re.compile(r"\n?\\begin{thebibliography}.*?\\end{thebibliography}", re.DOTALL)
include_or_input_pattern = re.compile(r"\n?(\\input|\\include|\\usepackage).*")
equation_pattern = re.compile(r"\n?\\begin{equation\*?}.*?\\end{equation\*?}", re.DOTALL)
align_pattern = re.compile(r"\n?\\begin{align\*?}.*?\\end{align\*?}", re.DOTALL)



def preprocess_tex_content(tex_content: str):
    # 预处理tex文件，主要有以下几个操作：
    # 1. 清除tex文件的所有注释
    # 2. 将多于2个的连续换行符更改为2个
    # 3. 将\input, \include, \begin{thebibliography}, \usepackage等不需要翻译的行/块单独提出
    # 4. 宏注入，为第一个\use_package序列注入\usepackage{xeCJK}和\usepackage{amsmath}包以便能顺利编译中文
    tex_content = comment_pattern.sub("", tex_content)
    tex_content = consecutive_line_breaks_pattern.sub("\n\n", tex_content)

    # 占位符计数
    replace_holder_counter = -1
    holder_index_to_content = []

    def replacement_helper(match):
        nonlocal replace_holder_counter
        replace_holder_counter += 1
        holder_index_to_content.append(match.group(0).strip())
        return f'\nls_replace_holder_{replace_holder_counter}'

    # 开始替换
    tex_content = bibliography_pattern.sub(replacement_helper, tex_content)
    tex_content = equation_pattern.sub(replacement_helper, tex_content)
    tex_content = align_pattern.sub(replacement_helper, tex_content)
    tex_content = include_or_input_pattern.sub(replacement_helper, tex_content)

    # 注入中文宏
    for i, holder_content in enumerate(holder_index_to_content):
        if holder_content.startswith("\\usepackage"):
            holder_index_to_content[i] = "\\usepackage{xeCJK}\n\\usepackage{amsmath}\n" + holder_content
            break

    
    return tex_content, holder_index_to_content
