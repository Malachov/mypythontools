"""
Only internal helping module for other modules. Not supposed to be used by users.
"""
from pathlib import Path
import sys

# Root is usually current working directory, if not, use `set_root` function.
root_path = Path.cwd()


def set_root(set_root_path=None):
    """Root folder is inferred automatically if call is from git_hooks folder or from root (cwd).
    If more projects opened in IDE, root project path can be configured here.

    Args:
        root_path ((str, pathlib.Path)): Path to project root.
    """
    if set_root_path:
        root_path = Path(set_root_path)

    if not root_path.as_posix() in sys.path:
        sys.path.insert(0, root_path.as_posix())
