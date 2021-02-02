"""
Only internal helping module for other modules. Not supposed to be used by users.
"""
from pathlib import Path
import sys

# Try to find root folder of python project based on where the script run
root_path = Path.cwd()

if not (root_path / 'docs').exists():
    root_path = root_path.parent

if not root_path.as_posix() in sys.path:
    sys.path.insert(0, root_path.as_posix())
