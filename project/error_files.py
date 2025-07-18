import sys
sys.path.append("/data1/zhangty25/LLM-Application")

import json
from typing import Iterable, Optional, List, Dict, Any

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionToolParam, ChatCompletionMessageParam
import httpx
from pathlib import Path

from common.llm import LLMConfig, GenerationOptions as LLMGenerationOptions
from llm.sync_client import sync_request_llm
import re
import random
import time



# import json files
with open("/data1/zhangty25/LLM-Application/project/original.json", "r") as f:
    data = json.load(f)


# function function
def write_error_to_jsonl(output: dict, path: str):
    """Appends a single error output (as a JSON object) to a .jsonl file."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(output + ",\n")


exception_types = [
    "ArithmeticError", "FloatingPointError", "OverflowError", "ZeroDivisionError",
    "AssertionError", "AttributeError", "BufferError", "ImportError",
    "ModuleNotFoundError", "IndexError", "KeyError", "MemoryError", "NameError",
    "UnboundLocalError", "BlockingIOError", "ChildProcessError", "ConnectionError",
    "BrokenPipeError", "ConnectionAbortedError", "ConnectionRefusedError",
    "ConnectionResetError", "FileExistsError", "FileNotFoundError", "InterruptedError",
    "IsADirectoryError", "NotADirectoryError", "PermissionError", "ProcessLookupError",
    "TimeoutError", "ReferenceError", "RuntimeError", "NotImplementedError",
    "RecursionError", "SyntaxError", "IndentationError", "SystemError", "TypeError", "ValueError",
    "UnicodeError", "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeTranslateError"
]



# helper function
def err_calls(query: str, tools: List[Dict[str, Any]], answers: List[Dict[str, Any]]):
    # Local vLLM configuration
    llm_config = LLMConfig(
        base_url="http://localhost:8003/v1",
        model="/home/zhangty25/.cache/modelscope/hub/models/qwen/Qwen3-8B",
        api_key="no-key-required"
    )

    # Generation options
    gen_config = LLMGenerationOptions(
        temperature=0.1,
        max_tokens=700
    )

    chosen_exception = random.choice(exception_types)

    messages: List[ChatCompletionMessageParam] = [
    {
    "role": "user",
    "content": f"""
You are a tool call corruptor.

Your job: Given a list of correct tool calls and their corresponding function definitions, select one tool call and corrupt it by introducing a single, realistic error that would cause it to fail.

---

### Guidelines:
- Introduce exactly **one** error of type **{chosen_exception}**.
- Do **not** generate any other kind of error.
- Ensure the corrupted tool call is still **plausible and structurally valid** — the error should arise from a semantic issue, not broken formatting.
- Ensure the error is realistically tied to the usage of parameters and their types as defined in `tool_info`.

---

### Parameter Consistency Rules:
- Do **NOT** raise errors for parameters that are correctly named and typed as per `tool_info.parameters`.
- Do **NOT** reject a parameter's value type if it matches the `type` specified in the tool definition.
  - Example: If `tool_info.parameters["foo"].type == "str"`, then `"foo": "abc"` is always valid — do not raise TypeError on it.
- Do **NOT** fabricate or remove parameter names.
- Only raise `TypeError` if the parameter's value type **does not match** the declared type.
- Only raise `KeyError` for parameters that are **not listed** in `tool_info.parameters`.
- Only raise `ValueError` for semantically invalid values (e.g., unsupported enum, date out of range, wrong format).
- Only raise `MissingRequiredArgument` (via KeyError or custom) if the parameter:
  - appears in `tool_info.parameters`
  - has **no default value**

---

### Input:

Query:
{query}

Tools:
{json.dumps(tools, indent=2)}

Correct Tool Calls:
{json.dumps(answers, indent=2)}

---

### Output:

Return a single corrupted tool call as a **raw JSON object** with exactly these keys:

- `error_info`: a realistic Python error message starting with **{chosen_exception}**
- `tool_name`: the name of the function being called.
- `tool_arguments`: the corrupted argument dictionary that would trigger the error.
- `tool_info`: the full original function definition from the tools list.

---

### Output Rules:
- **DO NOT** wrap the JSON in markdown or code fences.
- **JUST** return the corrupted JSON object and nothing else.
"""
}
]

    # Make the request
    response = sync_request_llm(
        llm_config=llm_config,
        messages=messages,
        generation_config=gen_config
    )

    # Parse and return the response content
    content = response.choices[0].message.content
    return content
    # try:
    #     return json.loads(content)
    # except Exception as e:
    #     print("[!] JSON parsing failed. Raw content below:")
    #     print(content)
    #     raise e


# helper function
def output_json(json_file):
    for sample in json_file:
        query = sample["query"]
        tools = json.loads(sample["tools"])
        answers = json.loads(sample["answers"])
        try:
            output = err_calls(query, tools, answers)
            write_error_to_jsonl(output,"/data1/zhangty25/LLM-Application/project/errors.json")
        except Exception as e:
            print("Error", {e})
        time.sleep(0.7)


if __name__ == "__main__":
    pass
    # # # Sample entry
    # sample = data[6]
    # query = sample["query"]
    # # Where can I find live giveaways for beta access and games?
    # tools = json.loads(sample["tools"])
    # # [{'name': 'live_giveaways_by_type', 'description': 'Retrieve live giveaways from the GamerPower API based on the specified type.', 'parameters': {'type': {'description': 'The type of giveaways to retrieve (e.g., game, loot, beta).', 'type': 'str', 'default': 'game'}}}]
    # answers = json.loads(sample["answers"])
    # [{'name': 'live_giveaways_by_type', 'arguments': {'type': 'beta'}}, {'name': 'live_giveaways_by_type', 'arguments': {'type': 'game'}}]
    # result = err_calls(query, tools, answers)
    # print(result)
    # write_error_to_jsonl(result, "/data1/zhangty25/LLM-Application/project/errors.json")

    # print(result)
    # print(json.dumps(result, indent=2))

    # test1="<think>\n</think>\n\n{\n  \"error_info\": \"TypeError: 'date' must be a string, not an integer.\",\n  \"tool_name\": \"historical\",\n  \"tool_arguments\": {\n    \"date\": 20230315\n  },\n  \"tool_info\": {\n    \"name\": \"historical\",\n    \"description\": \"Fetches the Fear and Greed Index for a given date from the RapidAPI service.\",\n    \"parameters\": {\n      \"date\": {\n        \"description\": \"The date for which to retrieve the index, in the format 'YYYY-MM-DD'.\",\n        \"type\": \"str\",\n        \"default\": \"2022-06-01\"\n      }\n    }\n  }\n}"
    # print(convert_json(test1))
    # output_json(data[125:275])

# be able to call API
# function to generate erroneous messages via API call (given json file input)
# function output erroneous messages with all these values included:
# error_info: Exception, tool_name: str, tool_arguments: Dict, tool_info: FunctionDefinition
# tool_name is True, tool_arguments may be Wrong, you need to fix it according to tool_info and error_info


# print(query, tools, answers)
