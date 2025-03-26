"""\
封装使用异步调用的LLM API调用类

Usage: 在QPS不超限情况下用异步尽快完成调用
"""

import asyncio
from openai import AsyncOpenAI
import sys
import re

from typing import Any, List, Optional, Union
from .config import config

# 避免windows下事件循环的异常
import platform
if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class RetryException(Exception):
    """重试的异常类"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code
    

class Translator:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.end_point, 
        )

        # 并发锁
        self.rate_limiter = None

        # 翻译的prompt
        self.system_prompt = config.system_prompt
        self.prompt_template = config.prompt_template

        # cot的prompt
        self.cot_prompt = config.cot_prompt_template

        # 记录一下总请求数和已完成请求数，用户友好交互
        self.num_of_requests = 0
        self.num_of_completed_requests = 0

    async def translate(self, text, language_to):
        # 选择是否使用COT
        if not config.use_cot:
            system_prompt = self.system_prompt
            prompt = self.prompt_template.format(language_to, text)
        else:
            system_prompt = ""
            prompt = self.cot_prompt.format(language_to, text)

        async with self.rate_limiter:
            completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    }, 
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=config.llm_model,
                temperature=config.temperature,
                top_p=config.top_p
            )

        self.num_of_completed_requests += 1
        # 每完成5个请求打印一下进度
        if self.num_of_completed_requests % 5 == 0:
            print(f"请求API中... 进度: {self.num_of_completed_requests} / {self.num_of_requests}")
        # 如果是COT取请求还得处理一下
        content = completion.choices[0].message.content
        if config.use_cot:
            pattern = r'\[result\]\s*content\s*=\s*"""\s*\n?(.*?)\s*\n"""'
            # deepseek会出现奇怪的bug，就是会把最后的"""\n```变成```\n```，这边手动替换一下
            if content.endswith('\n```\n```'):
                content = content.rstrip('\n```\n```') + '\n"""\n```'

            result = re.search(pattern, content, re.DOTALL)
            if result:
                content = result.group(1)
            else:
                print("cot返回结果的格式错误!准备重试...")
                self.num_of_completed_requests -= 1
                raise RetryException("cot格式错误，重试请求...")

        return content
    
    async def _translate_batch(self, texts: List[str], language_to, max_epoches=10):
        undo_of_texts = [1] * len(texts)
        results = [None] * len(texts)
        epoch = 0

        # 创建并发锁，之前在循环外创建可能会报错
        self.rate_limiter = asyncio.Semaphore(config.num_concurrent)
        
        while sum(undo_of_texts) > 0 and epoch < max_epoches:
            task_list = []
            call_index_list = []
            for i, text in enumerate(texts):
                if undo_of_texts[i] == 1:
                    task_list.append(self.translate(text, language_to))
                    call_index_list.append(i)

            # 异步执行
            call_results = await asyncio.gather(*task_list, return_exceptions=True)

            # 将结果输入聚合到结果列表
            for i, call_result in enumerate(call_results):
                if isinstance(call_result, Exception):
                    # 引入责任链机制，所有的异常都可以认为有以下解决方案
                    # 即重试、回退、抛出异常
                    need_retry, need_backtracing, need_throw_exception = False, False, False

                    # 异常判断
                    if isinstance(call_result, RetryException):
                        need_retry = True
                    elif hasattr(call_result, 'status_code'):
                        if call_result.status_code == 429:
                            print(f"触发频次限制...如果频繁出现可能说明qps设置过大...")
                            need_retry = True
                        elif call_result.status_code == 400:
                            print(f"触发风控机制，该部分回退为原文...")
                            need_backtracing = True
                        else:
                            need_throw_exception = True
                    else:
                        # 这里是未知的错误，为了保证翻译正常进行仅打印该错误
                        # 同样如400错误一般将该部分回退为原文
                        print(f"未处理的异常: {call_result}")
                        need_backtracing = True

                    # 处理责任
                    if need_retry:
                        continue
                    elif need_backtracing:
                        task_index = call_index_list[i]
                        undo_of_texts[task_index] = 0
                        results[task_index] = texts[task_index]
                    elif need_throw_exception:
                        raise call_result
                else:
                    task_index = call_index_list[i]
                    undo_of_texts[task_index] = 0
                    results[task_index] = call_result
            
            # 进入下一个循环
            epoch += 1

        return results
  
    

    def translate_batch(self, texts: List[str], language_to):
        # 初始化请求数和完成情况
        self.num_of_requests = len(texts)
        self.num_of_completed_requests = 0
        # 异步请求
        print(f"开始请求API进行翻译，总请求数: {self.num_of_requests}")
        result = asyncio.run(self._translate_batch(texts, language_to))
        print(f"请求完成，开始执行后续操作...")

        return result