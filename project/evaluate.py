import sys
sys.path.append("/data1/zhangty25/LLM-Application")
import json

def check_fixed_matches_original(answers, tool_name, fixed_args):
        answers_list = json.loads(answers)
        fixed_args = json.loads(fixed_args)
        original_args = [item["arguments"] for item in answers if item["name"] == tool_name]
        return any(fixed_args == orig for orig in original_args)


def calculate_accuracy(original_args_list, fixed_args_list, errors_list):
    assert len(original_args_list) == len(fixed_args_list) == len(errors_list)
    matches = 0
    for orig, fixed, error in zip(original_args_list, fixed_args_list, errors_list):
        answers=orig["answers"]
        tool_name=error["tool_name"]
        if check_fixed_matches_original(answers,tool_name, fixed):
            matches += 1
    return matches / len(original_args_list)



if __name__ == "__main__":
    with open("/data1/zhangty25/LLM-Application/project/Qwen3-4B/fixed_qwen3-4b.json", "r") as f:
        fixed = json.load(f)

    with open("/data1/zhangty25/LLM-Application/project/original.json", "r") as f:
        original = json.load(f)

    with open("/data1/zhangty25/LLM-Application/project/Qwen3-4B/errors_qwen3-4b.json", "r") as f:
        errors = json.load(f)

    # sample =errors[0]
    # fixed1=fixed[0]
    # print(set(sample["tool_info"].get("parameters").keys()))
    # print(set(fixed1.keys()))
    # for obj in errors:
    #     keys = obj["tool_info"].get("parameters").keys()
    #     keys=set(keys)
    #     for thing in fixed:
    #         if not keys.issuperset(set(thing.keys())):
    #             print(obj)
    #             print(thing)

    import json
    import os
    from pathlib import Path

    def extract_comparable_data(json_data, file_type):
        """Extract comparable elements based on file type"""
        if file_type == "original":
            # Parse stringified JSON fields if they exist
            tools = []
            if 'tools' in json_data:
                try:
                    tools_data = json.loads(json_data['tools']) if isinstance(json_data['tools'], str) else json_data['tools']
                    tools = [item['name'] for item in tools_data if 'name' in item]
                except (json.JSONDecodeError, TypeError):
                    pass

            answers = []
            if 'answers' in json_data:
                try:
                    answers_data = json.loads(json_data['answers']) if isinstance(json_data['answers'], str) else json_data['answers']
                    answers = [item['name'] for item in answers_data if 'name' in item]
                except (json.JSONDecodeError, TypeError):
                    pass

            return set(tools + answers)

        elif file_type == "error":
            if 'tool_name' in json_data:
                return {json_data['tool_name']}
            return set()

        elif file_type == "fixed":
            # Add logic for fixed format if needed
            return set()

        return set()

    def compare_json_sets(directory1, type1, directory2, type2):
        """Compare two directories of different JSON formats"""
        dir1 = Path(directory1)
        dir2 = Path(directory2)

        # Find matching filenames between directories
        files1 = {f.stem: f for f in dir1.glob('*.json')}
        files2 = {f.stem: f for f in dir2.glob('*.json')}
        common_files = set(files1.keys()) & set(files2.keys())

        comparison_results = {
            'in_both_dirs': [],
            'only_in_dir1': list(set(files1.keys()) - set(files2.keys())),
            'only_in_dir2': list(set(files2.keys()) - set(files1.keys())),
            'matches': []
        }

        for filename in common_files:
            with open(files1[filename]) as f1, open(files2[filename]) as f2:
                data1 = json.load(f1)
                data2 = json.load(f2)

                set1 = extract_comparable_data(data1, type1)
                set2 = extract_comparable_data(data2, type2)

                comparison_results['matches'].append({
                    'filename': filename,
                    f'{type1}_items': list(set1),
                    f'{type2}_items': list(set2),
                    'common_items': list(set1 & set2),
                    'unique_to_first': list(set1 - set2),
                    'unique_to_second': list(set2 - set1)
                })

        return comparison_results

    # Example usage
    results = compare_json_sets(
        directory1="/data1/zhangty25/LLM-Application/project/original.json",
        type1='original',
        directory2="/data1/zhangty25/LLM-Application/project/Qwen3-4B/errors_qwen3-4b.json",
        type2='error'
    )

    # Save results
    with open('/data1/zhangty25/LLM-Application/project/comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Comparison complete. Results saved to comparison_results.json")



    # print(calculate_accuracy(original, fixed, errors))
    # Save the filtered original examples
    # with open("/data1/zhangty25/LLM-Application/project/original.json", "w") as f:
    #     json.dump(matched_originals, f, indent=2)


    # Example usage:
    # answers_str = '[{"name": "live_giveaways_by_type", "arguments": {"type": "beta"}}, {"name": "live_giveaways_by_type", "arguments": {"type": "game"}}]'
    # fixed_args = '{"type": "beta"}'
    # tool_name = "live_giveaways_by_type"

    # print(check_fixed_matches_original(answers_str, tool_name, fixed_args))
    # Output: True
