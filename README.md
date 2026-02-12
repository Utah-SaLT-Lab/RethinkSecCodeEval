# Rethink_Sec_Code_Eval
Unit test for the code generated on SecCodePLT.

The Link to the paper: https://arxiv.org/pdf/2503.15554?

<!--ts-->
   * [Directory Structure](#directory-dtructure)
   * [Installation](#installation)
   * [Code Generation](#code-generation)
   * [Preprocessing](#preprocessing)
   * [Running the Test](#running-the-unit-test)
   * [Get The Result](#get-the-result)
   * [Citation](#citation)
<!--te-->

## Directory Structure
```
Rethink_Sec_Code_Eval
│   README.md
│   requirements.txt
|   Dockerfile   
│   ...
└───utils
│   │  SecPLT_func_name.json  
│  
│   
│   
└───Data
    │   results/
    │   summary/
│   └───unittest
|       └───000f5e47
│       │   setup.py
│       │   test_case.py
│
```

## Installation

⚠️ Since the code may contain security-related operations, such as `rm -rf`, it is highly recommended to run the tests in a containerized environment. We provide a Dockerfile for the container setup. Below, we provide an example using CharlieCloud to run the unit tests in a container. You can also use the Docker command, as we provide a Dockerfile for constructing the container.

The default img directory for CharlieCloud is /tmp, which may cause storage space issues. To prevent this, you can set the directory to a different location.

`CH_IMAGE_STORAGE=/path/to/a/desired/place`

If you encounter any issue when using Charliecloud, you may be able to find some solutions here: https://hpc.github.io/charliecloud/faq.html
1. Build the container

```
ch-image build -t test-runner -f Dockerfile .
```
2. Package Installation

```
pip install -r requirements.txt
```
## Code Generation

To generate the code, you can download the instruction prompt from the original **SecCodePLT Hugging Face Space**: https://huggingface.co/datasets/Virtue-AI-HUB/SecCodePLT.

⚠️ Please note that the original SecCodePLT contains 1,345 tasks. However, after unit test generation and filtering out samples with issues, we ultimately generated unit tests for 1,201 samples. As a result, we only support unit testing for these **1,201** tasks. The supported task IDs can be found in `utils/SecPLT_func_name.json`.

To execute the unit tests, you need to store the generated code in a **.jsonl** file following this format:

```
{"task_id": <id of the SecCodePLT sample>, "solution": <Generated Code>}

# Example:

{"task_id": "134f1a9c", "solution": def derive_hash(algorithm_name: str, input_data: bytes) -> bytes:...}
```

### Note:
Ensure you select the correct prompt template based on the model you are using (e.g., ChatGPT-style, CodeLLaMA-style, Qwen-style). Different models may require slightly different prompt formats (such as including explicit function signatures, docstrings, or problem descriptions). Using the wrong prompt format may lead to invalid or incomplete solutions, which will fail preprocessing or unit testing.

## Preprocessing

Before running the unit test, please run the preprocessing script to distribute the code into each unit test folder

```
python preprocess.py --model <Any name you want> --file_path <path to the jsonl file that store the code>

# Example
python preprocess.py --model qwen --file_path code.jsonl
```

## Running the Unit Test

```
sh run.sh <the name you just put after the --model>

#Example
sh run.sh qwen
```

## Get the Result

```
python get_result.py data/answer.json data/results/<the name you put after run.sh>_SecPLT_results.json --output <path to store the result>

# Example
python get_result.py data/answer.json data/results/qwen_SecPLT_results.json --output eval_result/qwen_eval_result.json
```

## Citation
```
@article{dai2025comprehensive,
  title={A Comprehensive Study of LLM Secure Code Generation},
  author={Dai, Shih-Chieh and Xu, Jun and Tao, Guanhong},
  journal={arXiv preprint arXiv:2503.15554},
  year={2025}
}
```
