"""Module with functions for 'misc' subpackage."""

from __future__ import annotations
from typing import Callable, Any, Iterable
import builtins
import time
import sys
from pathlib import Path
import os
import importlib.util
import subprocess

import pandas as pd
from tabulate import tabulate

import mylogging

from ..paths import PathLike, validate_path


class Emojis:
    """Emojis that can be printed."""

    PARTY = "🎉"  # "\U0001F389"
    DISAPPOINTMENT = " ☹️ "  # "\U0001F641"


EMOJIS = Emojis()


class GlobalVars:
    """Global variables that can be useful."""

    @property
    def jupyter(self):
        """If runs in Jupyter, it returns True."""
        return True if hasattr(builtins, "__IPYTHON__") else False

    @property
    def is_tested(self):
        """If is tested with Pytest, it returns True."""
        return True if "PYTEST_CURRENT_TEST" in os.environ else False


GLOBAL_VARS = GlobalVars()

DEFAULT_TABLE_FORMAT = {
    "tablefmt": "grid",
    "floatfmt": ".3f",
    "numalign": "center",
    "stralign": "center",
}


class TimeTable:
    """Class that create printable table with spent time on various phases that runs sequentionally.

    Add entry when current phase end (not when it starts).

    Example:
        >>> import time
        ...
        >>> time_table = TimeTable()
        >>> time.sleep(0.01)
        >>> time_table.add_entry("First phase")
        >>> time.sleep(0.02)
        >>> time_table.add_entry("Second phase")
        >>> time_table.add_entry("Third phase")
        >>> time_table.finish_table()
        ...
        >>> print(time_table.time_table)
        +--------------+--------------+
        |     Time     |  Phase name  |
        +==============+==============+
        | First phase  |    0...
    """

    def __init__(self) -> None:
        """Init the table."""
        self.time_df: pd.DataFrame = pd.DataFrame()
        self.time_table: str = ""
        self.times: list[tuple[str, float]] = []
        self.last_time: float = time.time()

    def add_entry(self, phase_name: str) -> None:
        """Add new line to the Time table."""
        self.times.append((phase_name, round((time.time() - self.last_time), 3)))

    def finish_table(self, table_format: None | dict = None) -> None:
        """Create time table.

        Args:
            table_format (None | dict, optional): Dict of format settings used in tabulate. If None, default
                DEFAULT_TABLE_FORMAT is used. Defaults to None.
        """
        if not table_format:
            table_format = DEFAULT_TABLE_FORMAT

        self.add_entry("Completed")
        self.time_df = pd.DataFrame(self.times, columns=["Time", "Phase name"])
        self.time_table = tabulate(self.time_df.values, headers=list(self.time_df.columns), **table_format)


def check_library_is_available(name, message="default"):
    """Make one-liner for checking whether some library is installed.

    If running on venv, it checks only this venv, no global site packages.

    Args:
        name (str): Name of the library.
        message (str, optional): Message that will be printed when library not installed. Defaults to "default".

    Raises:
        ModuleNotFoundError: If module is installed, error is raised.

    Example:
        >>> check_library_is_available("typing_extensions")
        >>> check_library_is_available("not_installed_lib")
        Traceback (most recent call last):
        ModuleNotFoundError: ...
    """
    if message == "default":
        message = (
            f"Library {name} is necessary and not available. Some libraries are used in just for small"
            f"part of module, so not installed by default. Use \n\n\tpip install {name}\n\n"
        )

    if not importlib.util.find_spec(name):
        raise ModuleNotFoundError(message)


def check_script_is_available(name, install_library=None, message="default"):
    """Check if python script is available.

    This doesn't need to be installed in current venv, but anywhere on computer.

    Args:
        name (str): Name of the script. E.g "black'.
        install_library (str, optional): Install script with this library added to default message.
            Defaults to None.
        message (str, optional): Message that will be printed when library not installed.
            Defaults to "default".

    Raises:
        RuntimeError: If module is installed, error is raised.

    Example:
        >>> check_script_is_available("black")
        >>> check_script_is_available("not_existing_script")
        Traceback (most recent call last):
        RuntimeError: ...
    """
    if message == "default":
        message = f"Python script {name} is necessary and not available. "

    if install_library:
        message = message + f"To get this executable available, do \n\n\tpip install {name}\n\n"

    exists = False

    for i in ["--version", "--help", ""]:
        try:

            result = subprocess.run(
                f"{name} {i}", check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
            )

            if result.returncode == 0:
                exists = True

            break

        except Exception:
            pass

    if not exists:
        raise RuntimeError(mylogging.format_str(message))


def watchdog(timeout: int | float, function: Callable, *args, **kwargs) -> Any:
    """Time-limited execution for python function. TimeoutError raised if not finished during defined time.

    Args:
        timeout (int | float): Max time execution in seconds.
        function (Callable): Function that will be evaluated.
        *args: Args for the function.
        *kwargs: Kwargs for the function.

    Raises:
        TimeoutError: If defined time runs out.
        RuntimeError: If function call with defined params fails.

    Returns:
        Any: Depends on used function.

    Examples:
        >>> import time
        >>> def sleep(sec):
        ...     for _ in range(sec):
        ...         time.sleep(1)
        >>> watchdog(1, sleep, 0)
        >>> watchdog(1, sleep, 10)
        Traceback (most recent call last):
        TimeoutError: ...
    """
    old_tracer = sys.gettrace()

    def tracer(frame, event, arg, start=time.time()):
        """Sys trace helpers that checks the time for watchdog."""
        now = time.time()
        if now > start + timeout:
            raise TimeoutError("Time exceeded")
        return tracer if event == "call" else None

    try:
        sys.settrace(tracer)
        result = function(*args, **kwargs)

    except TimeoutError:
        sys.settrace(old_tracer)
        raise TimeoutError(
            "Timeout defined in watchdog exceeded.",
        )

    except Exception:
        sys.settrace(old_tracer)
        raise RuntimeError(
            f"Watchdog with function {function.__name__}, args {args} and kwargs {kwargs} failed."
        )

    finally:
        sys.settrace(old_tracer)

    return result


def delete_files(paths: PathLike | Iterable[PathLike]):
    """Delete file or Sequence of files. If no permissions or file is open, it passes without error."""
    if isinstance(paths, (Path, str, os.PathLike)):
        paths = [paths]

    for i in paths:
        try:
            validate_path(i).unlink()
        except (FileNotFoundError, OSError):
            pass


def print_progress(name: str, verbose: bool = True):
    """Print current step of some process.

    Divide it with newlines so it's more readable.

    Args:
        name (str): Name current step.
        verbose (bool): It is possible to turn off logging of progress with one parameter config value.
            Defaults to True.
    """
    if verbose:
        print(f"\n{name}\n")
