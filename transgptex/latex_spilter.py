"""\
切分tex文件为合适的长度的块

Usage: 切分tex文件为合适的长度的块，以免超出上下文长度
"""

def split_string(s, separators, K):
    def split_with_separator(s, sep):
        return s.split(sep)
    
    result = [s]
    
    for sep in separators:
        new_result = []
        for segment in result:
            if len(segment) > K:
                split_parts = split_with_separator(segment, sep)
                temp_str = ""
                for part in split_parts:
                    if len(temp_str) + len(part) + len(sep) <= K:
                        if temp_str:
                            temp_str += sep
                        temp_str += part
                    else:
                        if temp_str:
                            if sep in [".", "\n\n", ","]:
                                temp_str += sep
                            else:
                                part = sep + part
                            new_result.append(temp_str)
                        temp_str = part
                if temp_str:
                    new_result.append(temp_str)
            else:
                new_result.append(segment)
        result = new_result
    
    return result



class LatexTextSplitter:
    def __init__(self, chunk_size=4000) -> None:
        self.separators = [
                # 按章节、小节、小小节进行切分
                "\n\\chapter{",
                "\n\\section{",
                "\n\\subsection{",
                "\n\\subsubsection{",
                # 切分长列表
                "\n\\begin{enumerate}",
                "\n\\begin{itemize}",
                "\n\\begin{description}",
                "\n\\begin{list}",
                "\n\\begin{quote}",
                "\n\\begin{quotation}",
                "\n\\begin{verse}",
                "\n\\begin{verbatim}",
                # 其他的杂类
                "\n\\begin{align}",
                "\n\n", 
                "\n$$",
                # 按句子切分
                ".",
                ",",
            ]
        self.chunk_size = chunk_size
        
    def split_text(self, text):
        return split_string(text, self.separators, self.chunk_size)