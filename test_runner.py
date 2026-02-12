#!/usr/bin/env python3
import os
import sys
import traceback
import argparse
import importlib.util
import json
import jsonlines
import base64
from pathlib import Path
import multiprocessing

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that can handle bytes and other non-serializable types"""
    def default(self, obj):
        if isinstance(obj, bytes):
            return {
                "__bytes__": True,
                "value": base64.b64encode(obj).decode('ascii')
            }
        # Handle any other non-serializable types
        try:
            return repr(obj)
        except:
            return f"[Unserializable object of type {type(obj).__name__}]"

def run_function(func, params, result_queue):
    try:
        result = func(**params)
        result_queue.put(('s',result))
    except Exception as e:
        result_queue.put(('e', e))

def safe_execute(function, params, timeout=5):
    result_queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_function, args=(function, params, result_queue))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        return ('t',"Timeout occurred!")
    return result_queue.get() if not result_queue.empty() else ('n', "No result returned.")

def load_module_from_file(file_path, module_name):
    """Load a Python module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_test_case_folder(folder_path, test_name):
    """Run tests for a single test case folder"""
    task_id = os.path.basename(folder_path)
    print(f"Running test for task_id: {task_id}")
    
    # Initialize statistics counters
    total_tests = 0
    passed_tests = 0
    
    # Paths to test files
    setup_path = os.path.join(folder_path, "setup.py")
    test_case_path = os.path.join(folder_path, "test_case.py")
    test_code_path = os.path.join(folder_path, f"{test_name}_test_code.py")
    
    # Check if required files exist
    if not os.path.exists(test_case_path):
        return {
            "task_id": task_id,
            "status": "error",
            "error": f"test_case.py not found in {folder_path}",
            "statistics": {
                "total_tests": 0,
                "passed_tests": 0,
                "success_rate": 0
            }
        }
    
    if not os.path.exists(test_code_path):
        return {
            "task_id": task_id,
            "status": "error",
            "error": f"test_code.py not found in {folder_path}",
            "statistics": {
                "total_tests": 0,
                "passed_tests": 0,
                "success_rate": 0
            }
        }
    
    # Create a shared namespace for all modules
    namespace = {}
    
    # Load setup module if it exists
    if os.path.exists(setup_path):
        try:
            setup_module = load_module_from_file(setup_path, f"setup_{task_id}")
            # Add all setup module attributes to the namespace
            for name in dir(setup_module):
                # Skip private attributes
                if not name.startswith('__'):
                    namespace[name] = getattr(setup_module, name)
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "error",
                "error": f"Failed to load setup.py: {str(e)}",
                "traceback": traceback.format_exc(),
                "statistics": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "success_rate": 0
                }
            }
    
    # Load test case module
    try:
        test_case_module = load_module_from_file(test_case_path, f"test_case_{task_id}")
        function_name = getattr(test_case_module, "function", None)
        test_cases = getattr(test_case_module, "test_cases", None)
        
        if function_name is None:
            return {
                "task_id": task_id,
                "status": "error",
                "error": f"function name not defined in test_case.py",
                "statistics": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "success_rate": 0
                }
            }
        
        if test_cases is None:
            return {
                "task_id": task_id,
                "status": "error",
                "error": f"test_cases not defined in test_case.py",
                "statistics": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "success_rate": 0
                }
            }
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "error",
            "error": f"Failed to load test_case.py: {str(e)}",
            "traceback": traceback.format_exc(),
            "statistics": {
                "total_tests": 0,
                "passed_tests": 0,
                "success_rate": 0
            }
        }
    
    # Load test code module and execute it with the shared namespace
    try:
        # Load the code as a string first
        with open(test_code_path, 'r') as f:
            test_code = f.read()
        
        # Execute the code in the shared namespace
        exec(test_code, namespace)
        
        # Get the function from the namespace
        function = namespace.get(function_name)
        
        if function is None:
            return {
                "task_id": task_id,
                "status": "error",
                "error": f"Function '{function_name}' not found in test_code.py",
                "statistics": {
                    "total_tests": 0,
                    "passed_tests": 0,
                    "success_rate": 0
                }
            }
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "error",
            "error": f"Failed to load test_code.py: {str(e)}",
            "traceback": traceback.format_exc(),
            "statistics": {
                "total_tests": 0,
                "passed_tests": 0,
                "success_rate": 0
            }
        }
    
    # Prepare test assets
    assets_dir = os.path.join(folder_path, "assets")
    if os.path.exists(assets_dir):
        # Change current working directory to assets directory so test files can be found
        original_dir = os.getcwd()
        os.chdir(assets_dir)
    
    # Run the tests
    results = []
    try:
        for params in test_cases:
            total_tests += 1
            try:
                result = safe_execute(function, params)
                #result = function(**params)
                if result[0] == "e":
                    raise result[1]
                else:
                    result = result[1]
                try:
                    result_repr = repr(result)
                except:
                    result_repr = f"[Object of type {type(result).__name__}]"
                
                passed_tests += 1
                results.append({
                    "params": params,
                    "status": "success",
                    "result": result_repr,
                    "result_type": type(result).__name__
                })
            except Exception as e:
                results.append({
                    "params": params,
                    "status": "error",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                })
    finally:
        # Restore original working directory if changed
        if os.path.exists(assets_dir):
            os.chdir(original_dir)
    
    # Calculate success rate
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    return {
        "task_id": task_id,
        "status": "completed",
        "results": results,
        "statistics": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": round(success_rate, 2)
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Run Python test cases from folders')
    parser.add_argument('test_dir', help='Directory containing test case folders')
    parser.add_argument('--test_data', help="The method of the code to be tested.", default="func")
    parser.add_argument('--output', help='File to write results to (default: results.json)')
    parser.add_argument('--summary', help='File to write summary statistics to (default: summary.json)')
    parser.add_argument('--task-id', help='Specific task ID to test (optional)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.test_dir) or not os.path.isdir(args.test_dir):
        print(f"Error: Test directory {args.test_dir} not found or not a directory")
        sys.exit(1)
    
    # Find all test case folders
    if args.task_id:
        task_folders = [os.path.join(args.test_dir, args.task_id)]
        if not os.path.exists(task_folders[0]):
            print(f"Error: Specified task ID folder {args.task_id} not found")
            sys.exit(1)
    else:
        task_folders = [os.path.join(args.test_dir, d) for d in os.listdir(args.test_dir) 
                       if os.path.isdir(os.path.join(args.test_dir, d))]
        print("#Sample:",len(task_folders))
    # Run tests for each folder
    all_results = []
    #task_folders = task_folders[:5]
    for folder in task_folders:
        result = run_test_case_folder(folder, args.test_data)
        all_results.append(result)
    
    # Write results to file
    output_file = args.output or "results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, cls=CustomJSONEncoder)
    
    # Generate and write summary statistics
    summary = {
        "total_samples": len(all_results),
        "samples": []
    }
    
    total_overall_tests = 0
    total_overall_passed = 0
    
    for result in all_results:
        task_id = result["task_id"]
        stats = result.get("statistics", {"total_tests": 0, "passed_tests": 0, "success_rate": 0})
        
        # Add to overall totals
        total_overall_tests += stats["total_tests"]
        total_overall_passed += stats["passed_tests"]
        
        summary["samples"].append({
            "task_id": task_id,
            "total_tests": stats["total_tests"],
            "passed_tests": stats["passed_tests"],
            "success_rate": stats["success_rate"]
        })
    
    # Calculate overall success rate
    overall_success_rate = (total_overall_passed / total_overall_tests * 100) if total_overall_tests > 0 else 0
    
    summary["overall"] = {
        "total_tests": total_overall_tests,
        "passed_tests": total_overall_passed,
        "success_rate": round(overall_success_rate, 2),
        "average_tests_per_sample": round(total_overall_tests / len(all_results), 2) if len(all_results) > 0 else 0
    }
    
    # Write summary to file if requested
    summary_file = args.summary or "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, cls=CustomJSONEncoder)
    print(f"Summary statistics written to {summary_file}")
    
    print(f"\nTest execution completed. Results written to {output_file}")

if __name__ == "__main__":
    main()
