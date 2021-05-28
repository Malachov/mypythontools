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


def infer_type(s):
    try:
        s = float(s)
        if s // 1 == s:
            return int(s)
        return s
    except ValueError:
        return s
