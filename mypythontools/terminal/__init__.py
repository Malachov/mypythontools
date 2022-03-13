"""Wrap python subprocess with some extra stuff

You can find here formatting errors, resolving venv script paths, unifying syntax for linux and windows etc.
Main function is 'terminal_do_command'. Use strings as input and if there can be space in some command, use
'get_console_str_with_quotes'.
"""
from mypythontools.terminal.terminal_internal import (
    EXECUTABLE,
    get_console_str_with_quotes,
    PYTHON,
    SHELL_AND,
    terminal_do_command,
)

__all__ = [
    "EXECUTABLE",
    "get_console_str_with_quotes",
    "PYTHON",
    "SHELL_AND",
    "terminal_do_command",
]
