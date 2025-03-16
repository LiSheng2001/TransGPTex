"""\
预处理tex文件，将格式进行统一以便后续进行启发式的处理。

Usage: 预处理tex文件的函数
"""

from typing import Any, List, Dict, Union
import sys
import re
import os

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


def search_bib_tex(file_dir: str):
    # 查找当前目录下是否存在`.bib`文件
    for file in os.listdir(file_dir):
        if file.endswith(".bib"):
            return True
    
    return False

# 辅助的正则表达式
comment_pattern = re.compile(r"(?<!\\)%.*")
consecutive_line_breaks_pattern = re.compile(r"\n{3,}")
bibliography_pattern = re.compile(r"^[ \t]*\\begin{thebibliography}.*?\\end{thebibliography}[ \t]*",re.MULTILINE | re.DOTALL)
equation_pattern = re.compile(r"^[ \t]*\\begin{equation\*?}(?:(?!\\end{equation\*?}).)*\\end{equation\*?}[ \t]*(?=\s*(?:\n|\Z))", re.MULTILINE | re.DOTALL)
align_pattern = re.compile(r"^[ \t]*\\begin{align\*?}(?:(?!\\end{align\*?}).)*\\end{align\*?}[ \t]*(?=\s*(?:\n|\Z))", re.MULTILINE | re.DOTALL)
single_line_comments = re.compile(r'^\s*%.*\n?', re.MULTILINE) # 查找独立的单行注释
table_pattern = re.compile(r"^[ \t]*\\begin{(?:table|figure|axis)\*?}.*?\\end{(?:table|figure|axis)\*?}", re.MULTILINE | re.DOTALL) # 查找表格、图片和axis
pdfoutput_pattern = re.compile(r"\\pdfoutput=1")
# 将\usepackage, \def等可能跨越多行的命令使用find_scope的方式去替换
target_fn_names = ["input", "include", "usepackage", "def", "newcommand", "renewcommand", "let", "providecommand"]


# 搜索tex中的函数体，因为存在嵌套关系没办法用正则简单地解决，因此通过遍历进行嵌套匹配
def find_scopes(content, fn_name):
    """
    找到以 \fn_name 开头的作用域，并返回匹配的字符串列表。

    :param content: 输入的 LaTeX 文本内容（字符串）。
    :param fn_name: 要匹配的命令名称（如 "usepackage"）。
    :return: 匹配的作用域列表。
    """
    # 正则表达式匹配以 \fn_name 开头的行
    pattern = re.compile(rf"\s*\\{fn_name}\b")
    
    # 先通过集合来去重
    scopes = set()
    
    # 按行分割输入内容
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 如果当前行匹配 \fn_name
        if pattern.match(line):
            # 初始化作用域内容
            scope = line
            bracket_stack = []  # 用于跟踪未闭合的括号
            
            # 分析当前行的内容，寻找未闭合的括号
            for char in line:
                if char == '[':
                    bracket_stack.append('[')
                elif char == ']':
                    if bracket_stack and bracket_stack[-1] == '[':
                        bracket_stack.pop()
                elif char == '{':
                    bracket_stack.append('{')
                elif char == '}':
                    if bracket_stack and bracket_stack[-1] == '{':
                        bracket_stack.pop()
            
            # 如果还有未闭合的括号，继续读取后续行
            while bracket_stack and i + 1 < len(lines):
                i += 1
                next_line = lines[i]
                scope += "\n" + next_line
                
                # 继续分析后续行的内容
                for char in next_line:
                    if char == '[':
                        bracket_stack.append('[')
                    elif char == ']':
                        if bracket_stack and bracket_stack[-1] == '[':
                            bracket_stack.pop()
                    elif char == '{':
                        bracket_stack.append('{')
                    elif char == '}':
                        if bracket_stack and bracket_stack[-1] == '{':
                            bracket_stack.pop()
            
            # 将完整的作用域添加到结果列表
            scopes.add(scope)
        
        # 移动到下一行
        i += 1
    
    # 返回一个列表，按字符数从多到少排序以减少替换冲突
    return sorted(scopes, key=len, reverse=True)

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
    # 1. 清除tex文件的所有注释，但对于\author、\begin{table}代码块中的注释要执行严格清除减少编译错误
    # 2. 将多于2个的连续换行符更改为2个
    # 3. 将\input, \include, \begin{thebibliography}, \usepackage等不需要翻译的行/块单独提出
    # 4. 宏注入，为第一个\use_package序列注入\usepackage{xeCJK}和\usepackage{amsmath}包以便能顺利编译中文

    # 10.07更新，为了减少编译时带来的奇怪bug，统一严格移除单行注释
    tex_content = single_line_comments.sub("", tex_content)
    # 移除\pdfoutput=1
    tex_content = pdfoutput_pattern.sub("", tex_content)
    tex_content = consecutive_line_breaks_pattern.sub("\n\n", tex_content)

    # 占位符计数
    replace_holder_counter = -1
    holder_index_to_content = []

    def replacement_helper(match):
        nonlocal replace_holder_counter
        replace_holder_counter += 1
        holder_index_to_content.append(match.group(0).strip())
        return f'ls_replace_holder_{replace_holder_counter}'

    # 开始替换
    tex_content = bibliography_pattern.sub(replacement_helper, tex_content)
    tex_content = equation_pattern.sub(replacement_helper, tex_content)
    tex_content = align_pattern.sub(replacement_helper, tex_content)

    # 特殊命令替换
    for target_fn_name in target_fn_names:
        target_scopes = find_scopes(tex_content, target_fn_name)
        # 替换
        for target_scope in target_scopes:
            replace_holder_counter += 1
            # 替换时注意所有的scope遵循以行首开头并且以行末结尾，因此用`re`模块能更精准地替换
            # 避免出现有位置`\renewcommand{\arraystretch}{0.9}`
            # 导致把`\renewcommand{\arraystretch}{0.9} %`也部分替换了导致出错
            tex_content = re.sub(rf"^{re.escape(target_scope)}$", f"ls_replace_holder_{replace_holder_counter}", tex_content, flags=re.MULTILINE)
            holder_index_to_content.append(target_scope)

    # 注入中文宏
    for i, holder_content in enumerate(holder_index_to_content):
        if holder_content.startswith("\\usepackage"):
            holder_index_to_content[i] = "\\usepackage{xeCJK}\n\\usepackage{amsmath}\n" + holder_content
            break
    
    # 合并连续占位符
    tex_content = merge_placeholders(tex_content, holder_index_to_content)
    
    return tex_content, holder_index_to_content
