function = 'execute_shell_command'
test_cases = [{'command': 'echo', 'args': ['Hello', 'World']}, {'command': 'echo', 'args': ['SingleWord']}, {'command': 'echo', 'args': []}, {'command': 'ls', 'args': ['nonexistent_directory']}, {'command': 'invalid_command', 'args': []}, {'command': 'echo', 'args': ['$HOME', '$PATH']}, {'command': 'echo', 'args': ["'single_quoted'", '"double_quoted"']}]
