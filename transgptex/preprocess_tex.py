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
include_or_input_pattern = re.compile(r"\n?(\\input|\\include|\\usepackage|\\newcommand|\\def).*")
equation_pattern = re.compile(r"\n?\\begin{equation\*?}.*?\\end{equation\*?}", re.DOTALL)
align_pattern = re.compile(r"\n?\\begin{align\*?}.*?\\end{align\*?}", re.DOTALL)


def merge_placeholders(input_text: str, holder_index_to_content: List[str]):
    """\
    合并仅以"\n"分割的占位符，避免LLM操作时遇到大块的占位符时发生遗漏。
    """
    lines = input_text.split("\n")
    result = []
    prev_holder_index = None
    # 记录原先两个非空行之间的换行符数量
    temp_line_breaks = 0
    
    # 通过指针扫描的方式并合并
    for i in range(len(lines)):
        line = lines[i]

        if line == "":
            temp_line_breaks += 1
        else:
            # 看看上一个非空行是不是占位符开头的，是则吸收
            if line.startswith("ls_replace_holder_") and len(result) > 0 and result[-1].startswith("ls_replace_holder_"):
                # 吸收，注意更改上一个index对应的内容
                current_holder_index = int(line.replace("ls_replace_holder_", ""))

                # 将之前的占位符内容吸收到上一个的位置，注意恢复换行符
                for _ in range(temp_line_breaks + 1):
                    holder_index_to_content[prev_holder_index] += "\n"
                holder_index_to_content[prev_holder_index] += holder_index_to_content[current_holder_index]
            else:
                # 直接加入上一行的尾部，如果开头有换行符忽略掉
                if len(result) > 0:
                    result[-1] = result[-1] + "".join(["\n" for _ in range(temp_line_breaks)])

                # 这里需要额外判断一下该line是不是占位符，如果是则要记录对应的index
                if line.startswith("ls_replace_holder_"):
                    prev_holder_index = int(line.replace("ls_replace_holder_", ""))
                
                result.append(line)
            # 置空换行符
            temp_line_breaks = 0

    return "\n".join(result)


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
    
    # 合并连续占位符
    tex_content = merge_placeholders(tex_content, holder_index_to_content)
    
    return tex_content, holder_index_to_content
