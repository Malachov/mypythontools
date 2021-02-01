from pathlib import Path
import sys

# Try to find root folder of python project based on where the script run
root_path = Path.cwd()

if not (root_path / 'docs').exists():
    root_path = root_path.parent


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


set_root()
