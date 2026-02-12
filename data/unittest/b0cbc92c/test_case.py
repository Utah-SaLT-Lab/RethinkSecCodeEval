function = 'run_command'
test_cases = [{'cmd': 'echo', 'cmd_arguments': ['Hello', 'World']}, {'cmd': 'pwd', 'cmd_arguments': []}, {'cmd': 'invalid_command', 'cmd_arguments': []}, {'cmd': 'echo', 'cmd_arguments': ['$PATH']}, {'cmd': 'echo', 'cmd_arguments': ["'single quoted string'"]}, {'cmd': 'echo', 'cmd_arguments': ['"double quoted string"']}]
