#!/usr/bin/env python3
import json
import argparse
import os
import sys
from collections import defaultdict

def compare_results(ground_truth_path, new_results_path, output_path):
    """
    Compare new test results against ground truth results
    
    Args:
        ground_truth_path: Path to the ground truth results.json
        new_results_path: Path to the new results to compare
        output_path: Path to write the comparison results
    
    Returns:
        Dictionary with comparison statistics
    """
    # Load the ground truth results
    with open("data/answer.json", 'r') as f:
        ground_truth = json.load(f)
    
    # Load the new results
    with open(new_results_path, 'r') as f:
        new_results = json.load(f)
    
    # Map ground truth by task_id for easier lookup
    ground_truth_map = {result["task_id"]: result for result in ground_truth}
    
    # Initialize comparison results
    comparison_results = []
    statistics = {
        "total_tasks": len(new_results),
        "matching_tasks": 0,
        "missing_tasks": 0,
        "total_tests": 0,
        "matching_tests": 0,
        "mismatched_tests": 0,
        "by_task": {}
    }
    
    # Compare each task result
    print(len(new_results))
    for new_result in new_results:
        task_id = new_result["task_id"]
        task_comparison = {
            "task_id": task_id,
            "task_status": "missing_in_ground_truth",
            "matches": 0,
            "mismatches": 0,
            "total_tests": 0,
            "comparison_details": []
        }
        
        # Check if task exists in ground truth
        if task_id not in ground_truth_map:
            task_comparison["task_status"] = "missing_in_ground_truth"
            statistics["missing_tasks"] += 1
            comparison_results.append(task_comparison)
            continue
        
        gt_result = ground_truth_map[task_id]
        
        # Compare task status
        if new_result["status"] != gt_result["status"]:
            task_comparison["task_status"] = "status_mismatch"
            task_comparison["ground_truth_status"] = gt_result["status"]
            task_comparison["new_status"] = new_result["status"]
            if new_result["statistics"]["total_tests"] == 0 and gt_result["statistics"]["total_tests"] != 0:   
                statistics["total_tests"] += gt_result["statistics"]["total_tests"]
                statistics["mismatched_tests"] += gt_result["statistics"]["total_tests"]
            
                statistics["by_task"][task_id] = {
                    "total_tests": gt_result["statistics"]["total_tests"],
                    "matches": 0,
                    "mismatches": gt_result["statistics"]["total_tests"],
                    "match_percentage": 0
                }
            comparison_results.append(task_comparison)
            continue

    
        # If status is error, compare error message
        if new_result["status"] == "error":
            if new_result.get("error", "") == gt_result.get("error", ""):
                task_comparison["task_status"] = "success"
                task_comparison["matches"] = 1
                task_comparison["total_tests"] = 1
                statistics["matching_tasks"] += 1
                statistics["total_tests"] += 1
                statistics["matching_tests"] += 1
            else:
                task_comparison["task_status"] = "error_mismatch"
                task_comparison["mismatches"] = 1
                task_comparison["total_tests"] = 1
                task_comparison["ground_truth_error"] = gt_result.get("error", "")
                task_comparison["new_error"] = new_result.get("error", "")
                
                #print(gt_result["statistics"]["total_tests"])
                statistics["total_tests"] += 1
                statistics["mismatched_tests"] += 1
            
            comparison_results.append(task_comparison)
            continue
        
        # Format 1 - list of function/params objects with function and results
        if isinstance(new_result.get("results", []), list) and all(isinstance(r, dict) and "function" in r for r in new_result.get("results", [])):
            # Map ground truth results by function for easier lookup
            gt_function_results = {r["function"]: r for r in gt_result.get("results", [])}
            
            for function_result in new_result.get("results", []):
                function_name = function_result["function"]
                
                # Check if function exists in ground truth
                if function_name not in gt_function_results:
                    task_comparison["comparison_details"].append({
                        "function": function_name,
                        "status": "missing_in_ground_truth"
                    })
                    continue
                
                gt_function_result = gt_function_results[function_name]
                
                # Compare function results
                compare_function_results(
                    function_name,
                    gt_function_result.get("results", []),
                    function_result.get("results", []),
                    task_comparison,
                    statistics
                )
        
        # Format 2 - direct list of results
        elif isinstance(new_result.get("results", []), list) and all(isinstance(r, dict) and "params" in r for r in new_result.get("results", [])):
            # Compare results directly
            compare_function_results(
                "default",
                gt_result.get("results", []),
                new_result.get("results", []),
                task_comparison,
                statistics
            )
        
        task_comparison["task_status"] = "success" if task_comparison["mismatches"] == 0 else "partial_match"
        if task_comparison["mismatches"] == 0:
            statistics["matching_tasks"] += 1
        
        comparison_results.append(task_comparison)
        
        # Add per-task statistics
        statistics["by_task"][task_id] = {
            "total_tests": task_comparison["total_tests"],
            "matches": task_comparison["matches"],
            "mismatches": task_comparison["mismatches"],
            "match_percentage": (task_comparison["matches"] / task_comparison["total_tests"] * 100) if task_comparison["total_tests"] > 0 else 0
        }
    
    # Calculate overall statistics
    if statistics["total_tests"] > 0:
        statistics["match_percentage"] = (statistics["matching_tests"] / statistics["total_tests"]) * 100
    else:
        statistics["match_percentage"] = 0
    
    # Prepare final results
    final_results = {
        "statistics": statistics,
        "comparisons": comparison_results
    }
    
    # Write comparison results to file
    with open(output_path, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    return statistics

def compare_function_results(function_name, gt_results, new_results, task_comparison, statistics):
    """
    Compare function results between ground truth and new results
    """
    # Create mappings by param hash for better comparison
    gt_results_map = {}
    for i, result in enumerate(gt_results):
        param_hash = json.dumps(result.get("params", {}), sort_keys=True)
        gt_results_map[param_hash] = (i, result)
    
    new_results_map = {}
    for i, result in enumerate(new_results):
        param_hash = json.dumps(result.get("params", {}), sort_keys=True)
        new_results_map[param_hash] = (i, result)
    
    # Find matching params in both results
    all_params = set(gt_results_map.keys()) | set(new_results_map.keys())
    
    for param_hash in all_params:
        # Update total tests
        task_comparison["total_tests"] += 1
        statistics["total_tests"] += 1
        
        # If params only in one set
        if param_hash not in gt_results_map:
            task_comparison["comparison_details"].append({
                "function": function_name,
                "params": json.loads(param_hash),
                "status": "missing_in_ground_truth"
            })
            statistics["mismatched_tests"] += 1
            task_comparison["mismatches"] += 1
            continue
            
        if param_hash not in new_results_map:
            task_comparison["comparison_details"].append({
                "function": function_name,
                "params": json.loads(param_hash),
                "status": "missing_in_new_results"
            })
            statistics["mismatched_tests"] += 1
            task_comparison["mismatches"] += 1
            continue
        
        # Get corresponding results
        gt_idx, gt_result = gt_results_map[param_hash]
        new_idx, new_result = new_results_map[param_hash]
        
        # Compare status
        if gt_result["status"] != new_result["status"]:
            task_comparison["comparison_details"].append({
                "function": function_name,
                "params": json.loads(param_hash),
                "status": "status_mismatch",
                "ground_truth_status": gt_result["status"],
                "new_status": new_result["status"]
            })
            statistics["mismatched_tests"] += 1
            task_comparison["mismatches"] += 1
            continue
        
        # Compare success result or error message
        if gt_result["status"] == "success":
            # Compare result value
            if gt_result.get("result", "") != new_result.get("result", ""):
                task_comparison["comparison_details"].append({
                    "function": function_name,
                    "params": json.loads(param_hash),
                    "status": "result_mismatch",
                    "ground_truth_result": gt_result.get("result", ""),
                    "new_result": new_result.get("result", "")
                })
                statistics["mismatched_tests"] += 1
                task_comparison["mismatches"] += 1
            else:
                task_comparison["comparison_details"].append({
                    "function": function_name,
                    "params": json.loads(param_hash),
                    "status": "success"
                })
                statistics["matching_tests"] += 1
                task_comparison["matches"] += 1
        else:  # status is error
            # Compare error message
            if (new_result.get("error_type") != gt_result.get("error_type") and new_result.get("error", "") != gt_result.get("error", "")):

                task_comparison["comparison_details"].append({
                    "function": function_name,
                    "params": json.loads(param_hash),
                    "status": "error_mismatch",
                    "ground_truth_error": gt_result.get("error", ""),
                    "new_error": new_result.get("error", "")
                })
                statistics["mismatched_tests"] += 1
                task_comparison["mismatches"] += 1
            else:
                task_comparison["comparison_details"].append({
                    "function": function_name,
                    "params": json.loads(param_hash),
                    "status": "success"
                })
                statistics["matching_tests"] += 1
                task_comparison["matches"] += 1

def print_comparison_summary(statistics):
    """Print summary of comparison results to console"""
    
    print("\nComparison Summary:")
    print(f"Total tasks: {statistics['total_tasks']}")
    print(f"Matching tasks: {statistics['matching_tasks']}")
    print(f"Missing tasks: {statistics['missing_tasks']}")
    print(f"Total tests: {statistics['total_tests']}")
    print(f"Matching tests: {statistics['matching_tests']}")
    print(f"Mismatched tests: {statistics['mismatched_tests']}")
    print(f"Overall match percentage: {statistics['match_percentage']:.2f}%")
    

def main():
    parser = argparse.ArgumentParser(description='Compare test results against ground truth')
    parser.add_argument('ground_truth', help='Path to ground truth results.json')
    parser.add_argument('new_results', help='Path to new results.json to compare')
    parser.add_argument('--output', help='File to write comparison results to (default: comparison.json)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.ground_truth):
        print(f"Error: Ground truth file {args.ground_truth} not found")
        sys.exit(1)
    
    if not os.path.exists(args.new_results):
        print(f"Error: New results file {args.new_results} not found")
        sys.exit(1)
    
    output_file = args.output or "comparison.json"
    
    # Compare results
    print(f"Comparing results...")
    print(f"Ground truth: {args.ground_truth}")
    print(f"New results: {args.new_results}")
    
    statistics = compare_results(args.ground_truth, args.new_results, output_file)
    
    print(f"\nComparison completed. Results written to {output_file}")
    print_comparison_summary(statistics)

if __name__ == "__main__":
    main()
