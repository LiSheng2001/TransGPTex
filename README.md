# TransGPTex

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

TransGPTex 是一个用于将 LaTeX 文章翻译成中文(或者其他语言)并编译成 PDF 的工具。它通过使用大型语言模型 (LLM) 来实现高质量的翻译。

## 快速开始

要快速运行起来本项目，主要分成3个步骤，即安装项目、选择LLM、开始翻译。

### 安装项目
在安装本项目前，你需要一个`xelatex`环境以编译翻译后的tex项目。如果机器上没有`xelatex`环境，Windows下推荐手动安装`MikTex`，Linux下则推荐`sudo apt-get install texlive-xetex`。

之后，通过`pip`命令安装本项目：
```bash
pip install transgptex
```

如果：
```bash
xelatex --help
tgtex -h
```
两个命令都能正常看到参数说明则说明安装成功了。

### LLM选择

本项目需要请求 LLM 的 API 来驱动 LLM 完成翻译，因此对LLM的选择是在翻译之前必须考虑的问题。实惠可靠的 LLM 能减少翻译花费、提高产出翻译的质量。

截止2025年3月2日，比较推荐的 LLM 有：

|      模型名称      | 输入价格（元/1M tokens） | 输出价格（元/1M tokens） |
| :----------------: | :----------------------: | :----------------------: |
| Doubao-1.5-pro-32k |           0.8            |            2             |
|    DeepSeek v3     |            2             |            8             |
|    GPT-4o-mini     |        0.15*7=1.05       |         0.6*7=4.2        |
|     GLM-4-Air      |           0.5            |            0.5           |

需要获取LLM的模型名字、推理端点以及API KEY。这些可以在对应大模型的官网上面找到，如果使用的是第三方的中转站，可以在中转站上查找相关信息。

### 开始翻译
以`gpt-4o-mini`演示使用流程。

假设想翻译`https://arxiv.org/abs/1706.03762`这篇论文（即 *Attention Is All You Need* 这篇），可以在目标目录启动命令行，输入：

```bash
# 申请llm api key，windows使用set，linux使用export
export LLM_API_KEY="申请的llm api key"

# 翻译，使用gpt-4o-mini模型
tgtex https://arxiv.org/abs/1706.03762 -llm_model gpt-4o-mini -end_point {api端点 官方或者中转端点}
```

等待完成之后即可在Attention Is All You Need目录下找到编译好的pdf文件。如果产出的文件有错误，也可以在`translated_source`目录下找到翻译的tex项目，手动修复错误后编译出满意的pdf。因为latex项目的复杂性，很可能需要手动介入去修复项目代码中的一些问题。

也可以使用思维链(cot)来提升翻译性能，默认是关闭的以节省token。cot很玄学，也不一定就比让LLM直接翻译好。开启之后，会让LLM根据要翻译的段落先进行思考，思考之后再进行正式翻译，以减少LLM翻译的生硬感，提高LLM的准确性。
使用`--use_cot`开启思维链式翻译，目前比较推荐用deepseek的模型进行cot翻译。
```bash
# cot翻译，使用deepseek-chat模型
tgtex https://arxiv.org/abs/1706.03762 -o "paper title" -llm_model deepseek-chat -end_point {api端点 官方或者中转端点} --use_cot
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

## 基本命令
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
- `llm_model`: 选择使用的 LLM 模型。
- `end_point`: LLM 推理端点 URL。
- `num_concurrent`: LLM API 的每秒查询数，默认为 100。
- `api_key`: 请配置在环境变量`LLM_API_KEY`中。
- `language_to`: 将源文件翻译成什么语言，默认为`Chinese`。
- `use_cot`: 使用`--use_cot`开启思维链式翻译，目前比较推荐用deepseek的模型进行cot翻译。开启之后，会让LLM根据要翻译的段落先进行思考，思考之后再进行正式翻译，以减少LLM翻译的生硬感，提高LLM的准确性。目前的cot仅加入思考流程，未来可以考虑将论文标题和论文摘要当作上下文输入给模型，以让LLM感知到要翻译的论文片段对应的上下文信息。

如果使用其他模型可以修改`llm_model`和`end_point`来实现。比如使用`deepseek-v3`模型，则可以改为:
```bash
# 设置LLM API KEY
export LLM_API_KEY="deepseek api key"

# 调用deepseek模型进行翻译
tgtex https://arxiv.org/abs/paper_id -o output/path -llm_model deepseek-chat -end_point https://api.deepseek.com/v1
```

## 许可
TransGPTex 项目采用 MIT 许可证。