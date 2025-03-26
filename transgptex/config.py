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
    num_concurrent: int = 100
    chunk_size: int = 4000
    system_prompt: str = "You are a professional, authentic machine translation engine."
    prompt_template: str = """\
Translate the following source text to {0}, Output translation directly without any additional text. do not modify any latex command such as \section, \cite and equations.
Keep line breaks in the original text. Do not translate quotations, proper nouns, etc. `ls_replace_holder_` is a special placeholder, don't translate it and copy it exactly.

Source Text: 
=====source text start.
{1}
=====source text end.
Translated Text:\
"""
    use_cot: bool = False
    cot_prompt_template: str = """\
Translate the following LaTeX paper excerpt into {0}, ensuring that LaTeX commands remain untranslated to avoid compilation issues.  
Key points to note:  
1. Clearly identify the structure of the excerpt before translating it—what parts should and should not be translated. Additionally, think carefully about how to translate abstract sentences and vocabulary before starting the actual translation.  
2. Be mindful of symbol escaping after translation. For instance, "93 percent of the people" should be translated as "93\\%的人", using a backslash to avoid confusion with LaTeX’s comment symbol (%).  
3. `ls_replace_holder_` is a special placeholder, don't translate it and copy it exactly.
4. Think thoroughly to minimize errors in your final translation output.  

Finally, organize your thoughts and present the results in the specified format:  

```
[think]
content = \"\"\"
<Your thought process>
\"\"\"

[result]
content = \"\"\"
<Formal Chinese translation of the LaTeX excerpt>
\"\"\"
```

Below is the LaTeX paper excerpt:
\"\"\"
{1}
\"\"\"
"""
    temperature=0.2, 
    top_p=0.1, 
    fix_hyphen=True


config = Config()
