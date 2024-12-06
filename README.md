# TransGPTex

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

TransGPTex 是一个用于将 LaTeX 文章翻译成中文(或者其他语言)并编译成 PDF 的工具。它通过使用大型语言模型 (LLM) 来实现高质量的翻译。

## 快速开始

20240719更新：openai推出了便宜的gpt-4o-mini模型，速度快、在latex方面效果也很不错，因此之后打算迁移到默认以gpt-4o-mini模型为翻译后端的版本。

目前可以直接这样使用gpt-4o-mini作为翻译LLM：

```bash
# 申请llm api key，windows使用set，linux使用export
set LLM_API_KEY="申请的llm api key"

# 翻译，使用gpt-4o-mini模型
tgtex https://arxiv.org/abs/xxxx.xxxxx -o "paper title" -llm_model gpt-4o-mini -end_point {api端点 官方或者中转端点}
```

引入了思维链(cot)，默认是关闭的以节省token，毕竟cot很玄学，也不一定就比让LLM直接翻译好。开启之后，会让LLM根据要翻译的段落先进行思考，思考之后再进行正式翻译，以减少LLM翻译的生硬感，提高LLM的准确性。
目前的cot仅加入思考流程，未来可以考虑将论文标题和论文摘要当作上下文输入给模型，以让LLM感知到要翻译的论文片段对应的上下文信息。
使用`--use_cot`开启思维链式翻译，目前比较推荐用deepseek的模型进行cot翻译。
```bash
# cot翻译，使用deepseek-chat模型
tgtex https://arxiv.org/abs/xxxx.xxxxx -o "paper title" -llm_model deepseek-chat -end_point {api端点 官方或者中转端点} --use_cot
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