"""
Module where you can get paths used in your project or configure paths to be able other modules here
in mypythontools with PROJECT_PATHS. You can also use `find_path()` to find some path efficiently in
some folder, excluding some other inner folders (like venv, node_modules etc.).There is also function
to get desktop path in posix way.
"""

from mypythontools.helpers.paths.paths import find_path, get_desktop_path, validate_path, PROJECT_PATHS

__all__ = ["find_path", "get_desktop_path", "validate_path", "PROJECT_PATHS"]
