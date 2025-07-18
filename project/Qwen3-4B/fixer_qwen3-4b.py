import sys
sys.path.append("/data1/zhangty25/LLM-Application")

from typing import Dict

from openai.types.shared_params.function_definition import FunctionDefinition
import json
from typing import Iterable, Optional, List, Dict, Any

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionToolParam, ChatCompletionMessageParam
import httpx
from pathlib import Path

from common.llm import LLMConfig, GenerationOptions as LLMGenerationOptions
from llm.sync_client import sync_request_llm
import re
import time


# import json files
with open("/data1/zhangty25/LLM-Application/project/Qwen3-4B/errors_qwen3-4b.json", "r") as f:
    data = json.load(f)

llm_errors = [
    "TokenLimitExceededError",
    "RateLimitError",
    "ModelNotFoundError",
    "InferenceServerError",
    "EmptyOutputError",
    "TokenizerError",
    "ConnectionError",
    "TimeoutError",
    "AuthenticationError",
    "InvalidToolArgumentsError",
    "ValidationError"
]

def mock(
    error_info: Exception, tool_name: str, tool_arguments: Dict, tool_info: FunctionDefinition
):
    if error_info in llm_errors:
        print("Error: ", {error_info})
        return {}

    llm_config = LLMConfig(
        base_url="http://localhost:8006/v1",
        model="/home/zhangty25/.cache/modelscope/hub/models/Qwen/Qwen3-4B",
        api_key="no-key-required"
    )

    gen_config = LLMGenerationOptions(
        temperature=0.1,
        max_tokens=700
    )
    # tool_name is True, tool_arguments may be Wrong, you need to fix it according to tool_info and error_info
    # your mock logic

    messages: List[ChatCompletionMessageParam] = [
    {
        "role": "user",
        "content": f"""
You are a tool call fixer.

Your task is to correct the `tool_arguments` so that the tool call becomes valid, using the given `tool_info` and `error_info`.

---

### Instructions:
- Assume `tool_name` is correct.
- Assume `tool_info` is the complete function signature.
- Assume the error described in `error_info` is real and must be resolved.
- Return only the corrected `tool_arguments` — a valid JSON dictionary that would no longer raise the error described.

---

### Input:

tool_name: {tool_name}

tool_arguments (possibly invalid):
{json.dumps(tool_arguments, indent=2)}

tool_info (reference schema):
{json.dumps(tool_info, indent=2)}

error_info:
{error_info}

---

### Output:

Return only the corrected `tool_arguments` as a JSON dictionary. Do **not** include any text or explanation.
"""
    }
]


    response = sync_request_llm(
        llm_config=llm_config,
        messages=messages,
        generation_config=gen_config
    )

    content = response.choices[0].message.content
    try:
        fix_input_dict = json.loads(content)
    except Exception:
        fix_input_dict = {}

    # fix_input_dict = {}
    # if not resolve, return {}
    return fix_input_dict



def write_to_jsonl(output: dict, path: str):
    """Appends a single fixed output (as a JSON object) to a .jsonl file."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(output + ",\n")


# helper function
def output_json(json_file):
    for sample in json_file:
        error_info = sample["error_info"]
        tool_name = sample["tool_name"]
        tool_arguments = sample["tool_arguments"]
        tool_info = sample["tool_info"]
        try:
            result = mock(error_info, tool_name, tool_arguments, tool_info)
            result = json.dumps(result)
            write_to_jsonl(result, "/data1/zhangty25/LLM-Application/project/Qwen3-4B/fixed_qwen3-4b.json")
        except Exception as e:
            print("Error", {e})
        time.sleep(0.7)



if __name__ == "__main__":
    # sample = data[1]
    # error_info = sample["error_info"]
    # tool_name = sample["tool_name"]
    # tool_arguments = sample["tool_arguments"]
    # tool_info = sample["tool_info"]
    # result = mock(error_info, tool_name, tool_arguments, tool_info)
    # print(result)
    # query = sample["query"]
    # # Where can I find live giveaways for beta access and games?
    # tools = json.loads(sample["tools"])
    # # [{'name': 'live_giveaways_by_type', 'description': 'Retrieve live giveaways from the GamerPower API based on the specified type.', 'parameters': {'type': {'description': 'The type of giveaways to retrieve (e.g., game, loot, beta).', 'type': 'str', 'default': 'game'}}}]
    # answers = json.loads(sample["answers"])
    # [{'name': 'live_giveaways_by_type', 'arguments': {'type': 'beta'}}, {'name': 'live_giveaways_by_type', 'arguments': {'type': 'game'}}]
    # result = err_calls(query, tools, answers)
    # print(result)
    output_json(data[200:])
