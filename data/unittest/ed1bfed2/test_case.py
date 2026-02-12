function = 'run_shell_command'
test_cases = [{'cmd': 'echo', 'arguments': ['Hello', 'World']}, {'cmd': 'echo', 'arguments': []}, {'cmd': 'echo', 'arguments': ['Special&Chars', ';', '|', '&', '>', '<']}, {'cmd': 'invalid_command', 'arguments': []}, {'cmd': 'echo', 'arguments': ["'SingleQuote'"]}, {'cmd': 'echo', 'arguments': ['"DoubleQuote"']}, {'cmd': 'echo', 'arguments': ['Spaces In Argument']}]
