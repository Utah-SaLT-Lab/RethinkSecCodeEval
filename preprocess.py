import json
import re
import jsonlines
import argparse
import ast
import os

parser = argparse.ArgumentParser(description='Distribute the Code to unittest folder')
parser.add_argument('--model', type=str, help='code to be dist.')
parser.add_argument('--file_path', type=str, help="Path to the file store the code")

args = parser.parse_args()

# Unwanted tokens to remove
UNWANTED_TOKENS = [
    '<s> ', '<｜begin▁of▁sentence｜>', '</s>', '<｜end▁of▁sentence｜>', '<|endoftext|>', '<|im_end|>', '|assistant|', '```python', '```'
]

def remove_extra_preceeding_spaces(text):
    """Remove additional leading spaces from each line in the text."""
    text = text.strip("\n")
    first_line_content = text[:text.find("\n")] if text.find("\n")!=-1 else text 
    initial_line_additional_space_count = len(first_line_content)-len(first_line_content.strip())
    text = "\n".join(line[initial_line_additional_space_count:] for line in text.split("\n"))
    return text

def clean_text(text):
    """Preprocess the text and remove unwanted tokens from the code."""
    # If model generated content contains markdown 
    code_begin_idx = text.find("```")
    code_closing_idx = text.rfind("```")
    if code_begin_idx!=-1 and code_closing_idx!=-1:
        text = text[code_begin_idx:code_closing_idx+3]

    for token in UNWANTED_TOKENS:
        text = text.replace(token, '')
    return remove_extra_preceeding_spaces(text)

def extract_function_name(code_text):
    """Extract the first function name using regex."""
    match = re.search(r'def\s+(\w+)\s*\(', code_text)
    if match:
        return match.group(1)
    return None

func_name = {}
with open('utils/SecPLT_func_name.json', 'r') as f:
    func_name = json.load(f)

collection = {}
with jsonlines.open(args.file_path) as jf:
    for obj in jf:
        idx = obj["task_id"]
        sol = obj["solution"]
        collection[idx] = sol


for idx, solution in collection.items():
    cleaned_code = clean_text(solution)
    code_function_name = extract_function_name(cleaned_code)
    if idx not in func_name:
        continue
    target_function_name = func_name[idx]
    output_file = f"data/unittest/{idx}/{args.model}_test_code.py"
    if code_function_name != target_function_name:
        cleaned_code = re.sub(r'(def\s+)\w+(\s*\()', rf'\1{target_function_name}\2', cleaned_code, count=1)
    
    with open(output_file, 'w') as f:
        f.write(cleaned_code)

print("Code Processed!")
