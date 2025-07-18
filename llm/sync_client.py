import sys
sys.path.append("/data1/zhangty25/LLM-Application")

from typing import Iterable, Optional

import rich
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionToolParam, ChatCompletionMessageParam
import httpx

from common.llm import LLMConfig, GenerationOptions as LLMGenerationOptions
import time

def sync_request_llm(
    llm_config: LLMConfig,
    messages: Iterable[ChatCompletionMessageParam],
    tools: Optional[Iterable[ChatCompletionToolParam]] = None,
    generation_config: LLMGenerationOptions = LLMGenerationOptions()
) -> ChatCompletion:
    api_key = llm_config.api_key
    base_url = llm_config.base_url
    model_name = llm_config.model

    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=api_key, base_url=base_url, http_client=http_client)
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=generation_config.stream,
        temperature=generation_config.temperature,
        tools=tools,
        extra_body={
            "top_k": 20,
            "chat_template_kwargs": {"enable_thinking": False},
        },
        timeout=30,
        max_tokens=generation_config.max_tokens,
        top_p=generation_config.top_p,
        presence_penalty=generation_config.presence_penalty
    )  # type: ignore
    return completion

    # retries = 5
    # for attempt in range(retries):
    #     try:
    #         return client.chat.completions.create(
    #             model=model_name,
    #             messages=messages,
    #             stream=generation_config.stream,
    #             temperature=generation_config.temperature,
    #             tools=tools,
    #             extra_body={
    #                 "top_k": 20,
    #                 "chat_template_kwargs": {"enable_thinking": False},
    #             },
    #             timeout=30,
    #             max_tokens=generation_config.max_tokens,
    #             top_p=generation_config.top_p,
    #             presence_penalty=generation_config.presence_penalty
    #         )  # type: ignore
    #     except Exception as e:
    #         wait_time = 2 ** attempt
    #         print(f"[!] LLM call failed (attempt {attempt + 1}/{retries}): {e}")
    #         time.sleep(wait_time)
    # raise RuntimeError("LLM call failed after multiple retries")


if __name__ == "__main__":

    # result = sync_request_llm(
    #     llm_config=LLMConfig(
    #         api_key="AnpXAL97M888frrAHmrbHmrdFJs27wrKca776zmZ786zwPJ6MrdJ8Csr6p6wGB7RJ99xk41VF5FHrbrk8zFh86RH8p8bfnKSNrCDqjan8rTal6j2wsxV9lZrJ7VlRfPH",
    #         base_url="https://modelfactory.lenovo.com/service-large-168-1743666716725/llm/v1",
    #         model="Qwen2.5-72B"
    #     ),
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "You are a helpful assistant."
    #         },
    #         {
    #             "role": "user",
    #             "content": "What is the meaning of life?"
    #         }
    #     ],
    #     generation_config=LLMGenerationOptions(
    #         temperature=0.2
    #     )
    # )
    # rich.print(result)

    # Local vLLM configuration
    llm_config = LLMConfig(
        base_url="http://localhost:5000/v1",
        model="Qwen2.5-3B",
        api_key="no-key-required"
    )

    # Generation options
    gen_config = LLMGenerationOptions(
        temperature=0.2,
        max_tokens=150
    )

    # Test message
    messages = [{"role": "user", "content": "What is the meaning of life?"}]

    # Make the request
    response = sync_request_llm(
        llm_config=llm_config,
        messages=messages,
        generation_config=gen_config
    )

    # Print response
    rich.print(response.choices[0].message.content)
