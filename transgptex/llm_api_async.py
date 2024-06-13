"""\
封装使用异步调用的LLM API调用类

Usage: 在QPS不超限情况下用异步尽快完成调用
"""

import time
import asyncio
from openai import AsyncOpenAI
import os

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

    async def translate(self, text, language_to):
        system_prompt = self.system_prompt
        prompt = self.promt_template.format(language_to, text)

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
            temperature=0.01,
        )

        return completion.choices[0].message.content
    
    async def _translate_batch(self, texts: List[str], language_to, max_epoches=3):
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
                    # 待实现，主要是实现429的重试
                    if call_result.status_code == "429":
                        continue
                    else:
                        raise call_result
                else:
                    undo_of_texts[i] = 0
                    results[i] = call_result
            
            # 进入下一个循环
            epoch += 1

        return results
  
    

    def translate_batch(self, texts: List[str], language_to):
        # return asyncio.run(self._translate_batch(texts, language_to))
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._translate_batch(texts, language_to))