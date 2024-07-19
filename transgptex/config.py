"""\
全局配置类

Usage: 全局共享一个config实例，这样避免到处传参
"""

from dataclasses import dataclass
import os

@dataclass
class Config:
    llm_model: str = "gpt-4o-mini"
    end_point: str = "https://api.openai.com/v1/"
    api_key: str = os.environ.get("LLM_API_KEY")
    qps: int = 3
    chunk_size: int = 4000
    system_prompt: str = "You are a professional, authentic machine translation engine."
    promt_template: str = """\
Translate the following source text to {}, Output translation directly without any additional text. do not modify any latex command such as \section, \cite and equations.
Keep line breaks in the original text. Do not translate quotations, proper nouns, etc. `ls_replace_holder_` is a special placeholder, don't translate it and copy it exactly.

Source Text: 
=====source text start.
{}
=====source text end.
Translated Text:\
"""


config = Config()
