"""\
挑出Latex项目中值得翻译的文件，并且将不需要翻译的文件复制到输出路径中

Usage: 挑出Latex项目中值得翻译的文件，并调用translate_tex进行翻译。
"""

from .translate_tex import generate_tex_chunks, postprocess_tex_content
from .llm_api_async import Translator
import os
import shutil


def select_file(input_dir: str, output_dir: str, language_to: str):
    # 使用闭包的方式来统计整个项目的tex块数目
    file_path2tex_chunks_data = {}

    def _select_file(input_dir_: str, output_dir_: str):
        # 将tex文件进行翻译，其他文件直接复制
        # 如果有文件夹的情况，则需要递归处理
        # 先新建输出路径
        os.makedirs(output_dir_, exist_ok=True)

        for file in os.listdir(input_dir_):
            # 组合成真实路径
            abs_path = os.path.join(input_dir_, file)
            output_path = os.path.join(output_dir_, file)

            if os.path.isdir(abs_path):
                # 是文件夹直接递归处理
                _select_file(abs_path, os.path.join(output_dir_, file))
            else:
                # 这里是文件
                if file.endswith(".tex"):
                    # translate_single_tex(abs_path, output_dir, language_to)
                    tex_chunks, holder_index_to_content = generate_tex_chunks(abs_path)
                    # 送入file_path2tex_chunks_data中
                    file_path2tex_chunks_data[abs_path] = {
                        "tex_chunks": tex_chunks, 
                        "holder_index_to_content": holder_index_to_content, 
                        "output_path": output_path
                    }
                else:
                    # 直接复制过去
                    shutil.copyfile(abs_path, output_path)
    
    # 调用分析方法
    _select_file(input_dir, output_dir)

    # 整合整个项目的所有分块
    all_tex_chunks = []
    all_chunks_index2file_path = []
    for file_path in file_path2tex_chunks_data:
        tex_chunks = file_path2tex_chunks_data[file_path]["tex_chunks"]
        all_tex_chunks += tex_chunks
        all_chunks_index2file_path += [file_path for _ in range(len(tex_chunks))]

    # 实例化翻译器
    translator = Translator()

    # 异步翻译所有块
    all_translated_texts = translator.translate_batch(all_tex_chunks, language_to)

    # 把翻译后的分块分配到对应的文件中
    for i in range(len(all_tex_chunks)):
        file_path = all_chunks_index2file_path[i]

        if file_path2tex_chunks_data[file_path].get("translated_tex_texts", None) is None:
            file_path2tex_chunks_data[file_path]["translated_tex_texts"] = []
        
        file_path2tex_chunks_data[file_path]["translated_tex_texts"].append(all_translated_texts[i])


    # 后处理，并写入所有块
    for file_path, file_data in file_path2tex_chunks_data.items():
        postprocess_tex_content(file_data["translated_tex_texts"], file_data["tex_chunks"], 
                                file_data["holder_index_to_content"], file_data["output_path"])
