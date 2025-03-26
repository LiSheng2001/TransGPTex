提供一些`TransGPTex`进阶的使用方法，以下内容可能显得有些冗长而且繁杂。如果您有定制化的需求，可以参阅高级用法章节自行适配。

## 自定义提示词

内置的提示词已经能够完成本项目的基本功能，但一些用户希望自定义提示词以实现对术语的精准翻译等个性化需求。目前本项目支持在运行`tgtex`命令的目录（即唤出命令行的目录）下新建`prompts.toml`文件来自定义提示词。模板如下：

````toml
prompt_template = """
Translate the following source text to {0}, Output translation directly without any additional text. do not modify any latex command such as \\section, \\cite and equations.
Keep line breaks in the original text. Do not translate quotations, proper nouns, etc. `ls_replace_holder_` is a special placeholder, don't translate it and copy it exactly.

Source Text: 
=====source text start.
{1}
=====source text end.
Translated Text:
"""

system_prompt = """
You are a professional, authentic machine translation engine.
"""

cot_prompt_template = """
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
````

把上面代码块内容复制到新建的`prompts.toml`文件中（注意编码需要使用`UTF-8`编码），然后可以开始自己动手自定义提示词。在着手自定义前有几个需要注意的点：
1. 注意在不使用`--use_cot`时，起作用的是`prompt_template`和`system_prompt`两个提示词。其中`system_prompt`里面不会输入参数，简洁地描述翻译任务或者LLM要扮演的角色即可。而`prompt_template`会输入两个字段，其中`{0}`这个占位符是要翻译的目标语言，由`--language_to`参数指定，默认是`Chinese`。而`{1}`占位符则是输入要翻译的Latex代码片段。
2. 在使用`--use_cot`时，只需要定义`cot_prompt_template`，`{0}`和`{1}`占位符的输入也是目标语言和待翻译的Latex片段。但请注意，不管您怎么调整`cot`的方式，请确保最终翻译结果以：
    ```toml
    [result]
    content = """
    <翻译后的Latex片段>
    """
    ```
    这样的形式呈现，否则可能会导致解析翻译结果失败。
3. 本项目会在预处理阶段将一些不必翻译的命令处理为`ls_replace_holder_`+数字的形式，以防止LLM破坏Latex指令，你需要明确在指令中说明这样的占位符不需要翻译。简单一点的话可以保留：
    ```
    Keep line breaks in the original text. Do not translate quotations, proper nouns, etc. `ls_replace_holder_` is a special placeholder, don't translate it and copy it exactly.
    ```
    这行指令。
4. 如果你需要自定义术语表，可以在`prompt_template`或`cot_prompt_template`的指令部分加入所需要的术语，从而提示LLM按你的要求来个性化地翻译。

举一个示例来更直观地说明：如果我想指示LLM将术语`Test-Time Scaling`翻译成`测试时扩展`，将`Scaling Law`翻译成`缩放定律`。在不使用`--use_cot`的情况下，可以简单地修改`prompt_template`的指令部分：
```toml
prompt_template = """
Translate the following source text to {0}, Output translation directly without any additional text. do not modify any latex command such as \\section, \\cite and equations.
Keep line breaks in the original text. Do not translate quotations, proper nouns, etc. `ls_replace_holder_` is a special placeholder, don't translate it and copy it exactly.

=== SPECIAL INSTRUCTIONS ===
You MUST use the following translations for specific terms:
"Test-Time Scaling" => "测试时扩展"
"Scaling Law" => "缩放定律"
=== END INSTRUCTIONS ===


Source Text: 
=====source text start.
{1}
=====source text end.
Translated Text:
"""
```
可以发现在指令部分新增了`SPECIAL INSTRUCTIONS`部分，在该部分插入术语表指示LLM按规则翻译即可。