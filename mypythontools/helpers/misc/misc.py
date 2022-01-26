"""Module with functions for 'misc' subpackage."""

from __future__ import annotations
from typing import Callable, Any, Union
import builtins
import time
import sys
from pathlib import Path
import os
import importlib.util
import ast

from typeguard import check_type
from typing_extensions import Literal, get_origin, get_args

import pandas as pd
from tabulate import tabulate

import mylogging


class Global_vars:
    @property
    def JUPYTER(self):
        return True if hasattr(builtins, "__IPYTHON__") else False

    @property
    def IS_TESTED(self):
        return True if "PYTEST_CURRENT_TEST" in os.environ else False


GLOBAL_VARS = Global_vars()

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
        self.time_df: pd.DataFrame = pd.DataFrame()
        self.time_table: str = ""
        self.times: list[tuple[str, float]] = []
        self.last_time: float = time.time()

    def add_entry(self, phase_name: str) -> None:
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


class ValidationError(TypeError):
    pass


def validate(value, allowed_type: Any, name: str) -> None:
    """Type validation. It also works for Union and validate Literal values.

    Instead of typeguard validation, it define just subset of types, but is simplier
    and needs no extra import, therefore can be faster.

    Args:
        value (Any): Value that will be validated.
        allowed_type (Any, optional): For example int, str or list. It can be also Union
            or Literal. If Literal, validated value has to be one of Literal values.
            Defaults to None.
        name (str | None, optional): If error raised, name will be printed. Defaults to None.

    Raises:
        ValidationError: Type does not fit.

    # Examples:
    #     >>> from typing_extension import Literal
    #     ...
    #     >>> validate(1, int)
    #     >>> validate(None, list | None)
    #     >>> validate("two", Literal["one", "two"])
    #     >>> validate("three", Literal["one", "two"])
    #     Traceback (most recent call last):
    #     ValidationError: ...
    """

    check_type(value=value, expected_type=allowed_type, argname=name)

    # TODO Wrap error with colors and remove stack only to configuration line...
    # try:
    #     check_type(value=value, expected_type=allowed_type, argname=name)
    # except TypeError:

    #     # ValidationError(mylogging.format_str("validate"))

    #     raise


def small_validate(value, allowed_type: None | Any = None, name: str | None = None) -> None:
    """Type validation. It also works for Union and validate Literal values.

    Instead of typeguard validation, it define just subset of types, but is simplier
    and needs no extra import, therefore can be faster.

    Args:
        value (Any): Value that will be validated.
        allowed_type (Any, optional): For example int, str or list. It can be also Union or Literal.
            If Literal, validated value has to be one of Literal values. If None, it's skipped.
            Defaults to None.
        name (str | None, optional): If error raised, name will be printed. Defaults to None.

    Raises:
        TypeError: Type does not fit.

    Examples:
        >>> from typing_extensions import Literal
        ...
        >>> small_validate(1, int)
        >>> small_validate(None, Union[list, None])
        >>> small_validate("two", Literal["one", "two"])
        >>> small_validate("three", Literal["one", "two"])  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        ValidationError: ...
    """
    if allowed_type:
        # If Union
        if get_origin(allowed_type) == Union:

            if type(value) in get_args(allowed_type):
                return
            else:
                raise ValidationError(
                    mylogging.format_str(
                        f"Allowed type for variable '{name}' are {allowed_type}, but you try to set an {type(value)}"
                    )
                )

        # If Literal - parse options
        elif get_origin(allowed_type) == Literal:
            options = getattr(allowed_type, "__args__")
            if value in options:
                return
            else:
                raise ValidationError(
                    mylogging.format_str(
                        f"New value < {value} > for variable < {name} > is not in allowed options {options}."
                    )
                )

        else:
            if isinstance(value, allowed_type):  # type: ignore
                return
            else:
                raise ValidationError(
                    mylogging.format_str(
                        f"Allowed allowed_type for variable < {name} > is {allowed_type}, but you try to set an {type(value)}"
                    )
                )


def str_to_infer_type(string_var: str) -> Any:
    """Convert string to another type (for example to int, float, list or dict).

    Args:
        string_var (str): String that should be converted.

    Returns:
        Any: New inferred type.

    Examples:
        >>> type(str_to_infer_type("1"))
        <class 'int'>
        >>> type(str_to_infer_type("1.2"))
        <class 'float'>
        >>> type(str_to_infer_type("['one']"))
        <class 'list'>
        >>> type(str_to_infer_type("{'one': 1}"))
        <class 'dict'>
    """

    return ast.literal_eval(string_var)


def json_to_py(json: dict, replace_comma_decimal: bool = True, replace_true_false: bool = True) -> Any:
    """Take json and eval it from strings. If string to string, if float to float, if object then to dict.

    When to use? - If sending object as parameter in function.

    Args:
        json (dict): JSON with various formats as string.
        replace_comma_decimal (bool, optional): Some countries use comma as decimal separator (e.g. 12,3).
            If True, comma replaced with dot (Only if there are no brackets (list, dict...)
            and if not converted to number string remain untouched) . For example '2,6' convert to 2.6.
            Defaults to True
        replace_true_false (bool, optional): If string is 'false' or 'true' (for example from javascript),
            it will be capitalized first for correct type conversion. Defaults to True

    Returns:
        dict: Python dictionary with correct types.

    Example:
        >>> json_to_py({'one_two': '1,2'})
        {'one_two': 1.2}

    """

    import ast

    evaluated = json.copy()

    for i, j in json.items():

        replace_condition = isinstance(j, str) and "(" not in j and "[" not in j and "{" not in j

        if replace_comma_decimal and replace_condition:
            j = j.replace(",", ".")

        if replace_true_false and replace_condition:
            if j == "true":
                evaluated[i] = True
            if j == "false":
                evaluated[i] = False
            if j == "true" or j == "false":
                continue

        try:
            evaluated[i] = ast.literal_eval(j)
        except Exception:
            pass

    return evaluated


def str_to_bool(bool_str):
    """Convert string to bool. Usually used from argparse. Raise error if don't know what value.

    Possible values for True: 'yes', 'true', 't', 'y', '1'
    Possible values for False: 'no', 'false', 'f', 'n', '0'

    Args:
        bool_str (str):

    Raises:
        TypeError: If not one of bool values inferred, error is raised.

    Returns:
        bool: True or False

    Example:
        >>> str_to_bool("y")
        True

    Argparse example::

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--test",
            choices=(True, False),
            type=str_to_bool,
            nargs="?",
        )
    """

    if isinstance(bool_str, bool):
        return bool_str
    if bool_str.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif bool_str.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise TypeError("Boolean value expected.")


def check_library_is_available(name, message="default"):
    """Make one-liner for checking whether some library is installed.

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
            "part of module, so not installed by default. Use \n\n\t`pip install {name}`\n\n"
        )

    if not importlib.util.find_spec(name):
        raise ModuleNotFoundError(mylogging.format_str(message))


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
        "Helper."
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
            mylogging.format_str(
                "Timeout defined in watchdog exceeded.",
                caption="TimeoutError",
                level="ERROR",
            )
        )

    except Exception:
        sys.settrace(old_tracer)
        raise RuntimeError(
            mylogging.format_str(
                f"Watchdog with function {function.__name__}, args {args} and kwargs {kwargs} failed."
            )
        )

    finally:
        sys.settrace(old_tracer)

    return result


def get_console_str_with_quotes(string: str | Path):
    """In terminal if value or contain spaces, it's not taken as one param.
    This wraps it with quotes to be able to use paths and values as needed.

    Args:
        string (str, Path): String  to be edited.

    Returns:
        str: Wrapped string that can be used in terminal.
    """
    if isinstance(string, (Path)):
        string = string.as_posix()
    string = string.strip("'")
    string = string.strip('"')
    return f'"{string}"'
