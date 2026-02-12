function = 'run_shell_cmd'
test_cases = [{'cmd_name': 'echo', 'cmd_args': ['Hello', 'World']}, {'cmd_name': 'echo', 'cmd_args': []}, {'cmd_name': 'invalid_command', 'cmd_args': []}, {'cmd_name': 'echo', 'cmd_args': ['$PATH']}, {'cmd_name': 'echo', 'cmd_args': ["'single quotes'"]}, {'cmd_name': 'echo', 'cmd_args': ['"double quotes"']}, {'cmd_name': 'echo', 'cmd_args': ['special*chars!@#']}]
