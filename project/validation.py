import json

def parse_answers(answers_str):
    try:
        return json.loads(answers_str) if isinstance(answers_str, str) else answers_str
    except Exception as e:
        print(f"Failed to parse answers: {e}")
        return []

def make_hashable(val):
    if isinstance(val, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in val.items()))
    elif isinstance(val, list):
        return tuple(make_hashable(v) for v in val)
    else:
        return val

def serialize_args(args):
    return make_hashable(args)

def build_original_index(original_list):
    index = {}
    for item in original_list:
        answers = parse_answers(item.get("answers", "[]"))
        for ans in answers:
            tool = ans.get("name")
            args = ans.get("arguments", {})
            key = (tool, serialize_args(args))
            index[key] = item
    return index


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

# keep track of types of errors where model makes mistake/right
right={exception:0 for exception in exception_types}
wrong={exception:0 for exception in exception_types}

def calculate_accuracy_from_unaligned(original_list, error_list, fixed_list):
    original_index = build_original_index(original_list)

    matches = 0
    total = 0

    for error, fixed_args in zip(error_list, fixed_list):
        try:
            tool_name = error["tool_name"]
            fixed_args_dict = json.loads(fixed_args) if isinstance(fixed_args, str) else fixed_args
            key = (tool_name, serialize_args(fixed_args_dict))
            err = error.get("error_info", "")
            err=err.split()[0][:-1]

            if key in original_index:
                matches += 1
                if err in right:
                    right[err]+=1
            else:
                if err in wrong:
                    wrong[err]+=1
            total += 1
        except Exception as e:
            print(f"Skipping due to error: {e}")
            continue
    if total>0:
        percent=matches/total
        return (percent, right, wrong)
    else:
        return 0.0

# Load from files
with open("/data1/zhangty25/LLM-Application/project/original.json") as f:
    original_list = json.load(f)

with open("/data1/zhangty25/LLM-Application/project/Qwen3-8B/errors_qwen3-8b.json") as f:
    error_list = json.load(f)

with open("/data1/zhangty25/LLM-Application/project/Qwen3-8B/fixed_qwen3-8b.json") as f:
    fixed_list = json.load(f)

acc = calculate_accuracy_from_unaligned(original_list, error_list, fixed_list)
print(acc)

frequencies={exception:0 for exception in exception_types}
# statistics for each type of error
for obj in error_list:
    # get
    err = obj.get("error_info", "")
    err=err.split()[0][:-1]
    if err in frequencies:
        frequencies[err]+=1
# print(frequencies)
# print(len(frequencies))
