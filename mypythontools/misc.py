"""
Module with miscellaneous functions.
"""
import builtins
from pathlib import Path


_JUPYTER = 1 if hasattr(builtins, "__IPYTHON__") else 0


def get_desktop_path():
    """Get desktop path.

    Returns:
        Path: Return pathlib Path object. If you want string, use `.as_posix()`
    """
    return Path.home() / "Desktop"


def infer_type(string_var):
    import ast

    evaluated = string_var
    try:
        evaluated = ast.literal_eval(evaluated)
    except Exception:
        pass
    return evaluated


def json_to_py(json):
    """Take json and eval it from strings.
    If string to string, if float to float, if object then to dict.

    When to use? - If sending object as parameter in function.

    Args:
        json (dict): JSON with various formats as string.

    Returns:
        dict: Python dictionary with correct types.
    """

    import ast

    evaluated = json.copy()

    for i, j in json.items():
        try:
            evaluated[i] = ast.literal_eval(j)
        except Exception:
            pass

    return evaluated
