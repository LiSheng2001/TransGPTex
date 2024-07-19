"""\
根据输入URL下载arXiv论文的源码并解压，为后续翻译和编译工作铺路

Usage: 下载arXiv论文的tex源码
"""

import arxiv
import os
import tarfile

def get_arxiv_id(url: str):
    # 去除http/https
    if url.startswith("https://"):
        url = url.lstrip("https://")
    elif url.startswith("http://"):
        url = url.lstrip("https://")

    if url.startswith("arxiv.org/abs/"):
        arxiv_id = url.lstrip("arxiv.org/abs/")
    elif url.startswith("arxiv.org/pdf/"):
        arxiv_id = url.lstrip("arxiv.org/pdf/").replace(".pdf", "")
    else:
        # 这里可能是直接输入了arxiv id
        arxiv_id = url
    
    return arxiv_id


def get_paper_title(arxiv_id: str):
    paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
    return paper.title


def download_paper_source(arxiv_id: str, output_path: str, use_cache: bool=True):
    print(f"开始下载arXiv论文... arxiv_id: {arxiv_id}")
    paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
    
    if os.path.exists(os.path.join(output_path, f"{arxiv_id}.tar.gz")) and use_cache:
        print(f"检测到已下载源码，跳过下载...")
    else:
        paper.download_source(dirpath=output_path, filename=f"{arxiv_id}.tar.gz")
        print(f"论文源码下载成功!")


def extract_tar_gz(file_path, extract_path='.'):
    try:
        with tarfile.open(file_path, 'r:gz') as tar:
            tar.extractall(path=extract_path)
            print(f"文件解压到 {extract_path} 成功")
    except Exception as e:
        print(f"解压文件时发生错误: {e}")

