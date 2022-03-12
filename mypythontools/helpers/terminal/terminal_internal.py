"""Module with functions for 'terminal' subpackage."""

from __future__ import annotations
from pathlib import Path
import subprocess
import platform

from ..paths import PathLike


class TerminalCommandError(Exception):
    pass


SHELL_AND = " && " if platform.system() == "Windows" else " && "
"""If using some nonstandard shell can be edited here globally ';' can be used if && not working."""
EXECUTABLE = None if platform.system() == "Windows" else "/bin/bash"
"""To be able to use 'source' it points to '/bin/bash' on linux."""
PYTHON = "python" if platform.system() == "Windows" else "python3"


def terminal_do_command(
    command: str,
    shell: bool = True,
    cwd: None | PathLike = None,
    verbose: bool = True,
    error_header: str = "",
):
    """Run command in terminall and process output.

    Args:
        command (str): Command to run.
        shell (bool, optional): Same meaning as in ``subprocess.run()``. Defaults to False.
        cwd (None | PathLike, optional): Same meaning as in ``subprocess.run()``. Defaults to None.
        verbose (bool, optional): Whether print output to console. Defaults to True.
        error_header (str, optional): If meet error, message at the beginning of message. Default to "".

    Raises:
        RuntimeError: When process fails to finish or return non zero return code.
    """
    error = None

    try:
        result = subprocess.run(command, shell=shell, cwd=cwd, capture_output=True)
        if result.returncode == 0:
            if verbose:
                print(result.stdout.decode().strip("\r\n"))
        else:
            stderr = result.stderr.decode().strip("\r\n")
            stdout = result.stdout.decode().strip("\r\n")
            error = f"\n\nstderr:\n\n{stderr}\n\nstdout:\n\n{stdout}\n\n"

    except Exception:  # pylint: disable=broad-except
        error = "Suprocess command crashed internally in subprocess and did not finished."

    if error:
        header = f"{error_header}\n\n" if error_header else ""
        cwd_str = "on your project root" if cwd is None else f"in '{cwd}' folder"

        raise TerminalCommandError(
            f"{header}"
            f"Running command in terminal failed. Try command below in the terminal {cwd_str} "
            f"\n\n{command}\n\n"
            "On windows use cmd so script paths resolved correctly. Try it with administrator rights in\n"
            "your project root folder. Permission error may be one of the typical issue or some\n"
            "necessary library missing or installed elsewhere than in used venv.\n\n"
            f"Captured error: {error}",
        )


def get_console_str_with_quotes(string: PathLike):
    """In terminal if value or contain spaces, it's not taken as one param.

    This wraps it with quotes to be able to use paths and values as needed. Alternative to this function is to
    use python shlex library, list of commands and 'shlex.join' to get the command string.

    Args:
        string (str, Path): String  to be edited.

    Returns:
        str: Wrapped string that can be used in terminal.

    Example:
        >>> get_console_str_with_quotes("/path to file/file")
        '"/path to file/file"'
    """
    if isinstance(string, (Path)):
        string = string.as_posix()
    if not isinstance(string, str):
        string = str(string)
    string = string.strip("'")
    string = string.strip('"')
    return f'"{string}"'
