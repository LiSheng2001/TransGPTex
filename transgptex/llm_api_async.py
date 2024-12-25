"""\
封装使用异步调用的LLM API调用类

Usage: 在QPS不超限情况下用异步尽快完成调用
"""

import time
import asyncio
from openai import AsyncOpenAI
import os
import re

from typing import Any, List, Optional, Union
from .config import config

class RateLimiter:
    def __init__(self, rate: int):
        self.rate = rate
        self.tokens = rate
        self.last_check = time.monotonic()

    async def acquire(self):
        while self.tokens <= 0:
            await asyncio.sleep(0.1)
            now = time.monotonic()
            elapsed = now - self.last_check
            self.last_check = now
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
        
        self.tokens -= 1

class RetryException(Exception):
    """重试的异常类"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code

async def fetch(session, url, rate_limiter):
    await rate_limiter.acquire()
    async with session.get(url) as response:
        return await response.text()
    

class Translator:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.end_point, 
        )

        # QPS锁
        self.rate_limiter = RateLimiter(rate=config.qps)

        # 翻译的prompt
        self.system_prompt = config.system_prompt
        self.promt_template = config.promt_template

        # cot的prompt
        self.cot_prompt = config.cot_prompt_template

        # 记录一下总请求数和已完成请求数，用户友好交互
        self.num_of_requests = 0
        self.num_of_completed_requests = 0

    async def translate(self, text, language_to):
        # 选择是否使用COT
        if not config.use_cot:
            system_prompt = self.system_prompt
            prompt = self.promt_template.format(language_to, text)
        else:
            system_prompt = ""
            prompt = self.cot_prompt.format(language_to, text)

        # 请求锁
        await self.rate_limiter.acquire()

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
            pattern = r'\[result\]\s*content\s*=\s*"""\s*\n(.*?)\s*\n"""'
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
                    if isinstance(call_result, RetryException):
                        continue
                    elif call_result.status_code == 429:
                        print(f"触发频次限制...如果频繁出现可能说明qps设置过大...")
                        continue
                    elif call_result.status_code == 400:
                        print(f"触发风控机制，该部分回退为原文...")
                        task_index = call_index_list[i]
                        undo_of_texts[task_index] = 0
                        results[task_index] = texts[task_index]
                        continue
                    else:
                        raise call_result
                else:
                    task_index = call_index_list[i]
                    undo_of_texts[task_index] = 0
                    results[task_index] = call_result
            
            # 进入下一个循环
            epoch += 1

        return results
  
    

    def translate_batch(self, texts: List[str], language_to):
        # return asyncio.run(self._translate_batch(texts, language_to))
        # 初始化请求数和完成情况
        self.num_of_requests = len(texts)
        self.num_of_completed_requests = 0

        # 异步请求
        print(f"开始请求API进行翻译，总请求数: {self.num_of_requests}")
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self._translate_batch(texts, language_to))
        print(f"请求完成，开始执行后续操作...")

        return result