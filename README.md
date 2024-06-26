# TransGPTex

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

TransGPTex 是一个用于将 LaTeX 文章翻译成中文(或者其他语言)并编译成 PDF 的工具。它通过使用大型语言模型 (LLM) 来实现高质量的翻译。

## 快速开始

20240618更新：目前发现DeepSeek-V2-Coder模型在保留Latex代码方面比较优秀，翻译的Tex文件编译问题较glm-4-air和deepseek-v2-chat少。而且价格也依旧比较合理，因此之后打算迁移到默认以DeepSeek-V2-Coder模型为翻译后端的版本。

目前可以直接这样使用DeepSeek-V2-Coder作为翻译LLM：
```bash
# 申请deepseek api key
set LLM_API_KEY="申请的deepseek api key"

# 翻译，使用deepseek
tgtex https://arxiv.org/abs/xxxx.xxxxx -o "paper title" -llm_model deepseek-coder -end_point https://api.deepseek.com
```

## 功能特性

- 支持从 arXiv 直接下载 LaTeX 源码。
- 支持翻译单个 LaTeX 文件或整个 LaTeX 项目。
- 支持自定义翻译语言和翻译模型。
- 支持编译生成 PDF 文件。

## 安装

```bash
pip install transgptex
```

## 快速开始
通过命令行：
```bash
# 设置API key
export LLM_API_KEY="glm api key"

# 从 arXiv 翻译并编译整个文章项目
tgtex https://arxiv.org/abs/paper_id -o output/path

# 翻译整个 LaTeX 项目
tgtex --own_tex_project -o output/path path/to/your/latex/project

# 翻译单个 LaTeX 文件
tgtex --single_tex -o output.tex path/to/your/latex/file.tex

# 获取帮助
tgtex -h
```

几个核心的配置：
- `llm_model`: 选择使用的 LLM 模型，默认为 glm-4-air。
- `end_point`: LLM 推理端点 URL，默认为 https://open.bigmodel.cn/api/paas/v4/。
- `qps`: LLM API 的每秒查询数，默认为 5。
- `api_key`: 请配置在环境变量`LLM_API_KEY`中。

如果使用其他模型可以修改`llm_model`和`end_point`来实现。比如使用deepseek-v2模型，则可以改为:
```bash
# 设置LLM API KEY
export LLM_API_KEY="deepseek api key"

# 调用deepseek模型进行翻译
tgtex https://arxiv.org/abs/paper_id -o output/path -llm_model deepseek-chat -end_point https://api.deepseek.com/v1
```

## 许可
TransGPTex 项目采用 MIT 许可证。