"""
Module with miscellaneous functions. For example myproperty, which is decarator for creating
simplified properties or json_to_py that can convert json string to correct python types or
str_to_infer_type that will convert string to correct type.
"""

from __future__ import annotations
from typing import Callable, Any, cast
import builtins
import time
import sys
from pathlib import Path

import mylogging


_JUPYTER = 1 if hasattr(builtins, "__IPYTHON__") else 0


def validate(value, types: Any = None, options: list | None = None, name: str | None = None) -> None:
    """Validate type of variable and check if this variable is in defined options.

    Args:
        value (Any): Value that will be validated.
        types (Any, optional): For example int, str or list. It can be list of possible types. Defaults to None.
        options (list | None, optional): List of possible options. If value is not in options, error will be raised. Defaults to None.
        name (str | None, optional): If error raised, name will be printed. Defaults to None.

    Raises:
        TypeError: Type does not fit.
        KeyError: Value not in defined options.

    Examples:
        >>> validate(["one"], types=[list, tuple])
        >>> validate("two", options=["one", "two"])
        >>> validate("three", options=["one", "two"])
        Traceback (most recent call last):
        KeyError: ...
    """
    if types:

        # To be able to use None in types instead of type(None)
        if isinstance(types, (list, tuple)) and None in types:
            types = list(types)

            for i, j in enumerate(types):
                if j is None:
                    types[i] = type(None)

        if isinstance(types, list):
            types = tuple(types)

        if not isinstance(value, types):
            raise TypeError(
                mylogging.return_str(
                    f"Allowed types for variable < {name} > are {types}, but you try to set an {type(value)}"
                )
            )

    if options and value not in options:
        raise KeyError(
            mylogging.return_str(
                f"New value < {value} > for variable < {name} > is not in allowed options {options}."
            )
        )


def str_to_infer_type(string_var: str) -> Any:
    """Convert string to another type (for example to int, float, list or dict).

    Args:
        string_var (str): String that should be converted.

    Returns:
        Any: New infered type.

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
    import ast

    evaluated = string_var
    try:
        evaluated = ast.literal_eval(evaluated)
    except Exception:
        pass
    return evaluated


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
            mylogging.return_str(
                "Timeout defined in watchdog exceeded.",
                caption="TimeoutError",
                level="ERROR",
            )
        )

    except Exception:
        sys.settrace(old_tracer)
        raise RuntimeError(
            mylogging.return_str(
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
