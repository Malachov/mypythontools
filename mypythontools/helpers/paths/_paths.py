"""Module with functions for 'paths' subpackage."""

from __future__ import annotations
from typing import Sequence, Union
from pathlib import Path
import sys
import builtins
import os

import mylogging

from ..type_hints import validate_sequence

PathLike = Union[Path, os.PathLike, str]  # Path is included in PathLike
"""Str pr pathlib Path. It can be also relative to current working directory."""


class _ProjectPaths:
    """Define paths for usual python projects like root path, docs path, init path etc.

    You can find paths, that are lazy evaluated only after you ask for them. They are inferred
    automatically, but if you have alternative structure, you can also set it. Getters return path objects,
    so it's posix.

    Note:
        If you use paths in `sys.path.insert` or as subprocess main parameter, do not forget to convert it
        to string with `.as_posix()`.
    """

    def __init__(self) -> None:
        self._root = None
        self._app = None
        self._init = None
        self._tests = None
        self._docs = None
        self._readme = None

    def add_root_to_sys_path(self) -> None:
        """As name suggest, add root to sys.paths on index 0."""
        if self.root.as_posix() not in sys.path:
            sys.path.insert(0, self.root.as_posix())

    @property
    def root(self) -> Path:
        """Path where all project is (docs, tests...). Root is usually current working directory.

        Type:
            Path

        Default:
            Path.cwd()
        """
        # If not value yet, set it first
        if not self._root:
            new_root_path = Path.cwd()

            # If using jupyter notebook from tests - very specific use case
            if new_root_path.name == "tests" and hasattr(builtins, "__IPYTHON__"):
                new_root_path = new_root_path.parent

            self._root = new_root_path

        return self._root

    @root.setter
    def root(self, new_path: PathLike) -> None:
        self._root = validate_path(new_path)

    @property
    def init(self) -> Path:
        """Path to __init__.py.

        Type:
            Path

        Default:
            **/__init__.py
        """
        if not self._init:
            exclude = []
            for i in ["docs", "tests"]:
                try:
                    exclude.append(getattr(self, i))
                except AttributeError:
                    pass

            self._init = find_path(
                "__init__.py",
                self.root,
                exclude_paths=exclude,
            )

        return self._init

    @init.setter
    def init(self, new_path: PathLike) -> None:
        self._init = validate_path(new_path)

    @property
    def app(self) -> Path:
        """Folder where python scripts are (and __init__.py).

        Type:
            Path

        Default:
            __App_path
        """
        if not self._app:
            self._app = self.init.parent

        return self._app

    @app.setter
    def app(self, new_path: PathLike) -> None:
        self._app = validate_path(new_path)

    @property
    def tests(self) -> Path:
        """Folder where tests are stored. Usually root / tests.

        'test', 'Test', 'Tests', 'TEST', 'TESTS' also inferred if on root.

        Type:
            Path

        Default:
            root_path/tests
        """
        if not self._tests:
            for i in ["tests", "test", "Test", "Tests", "TEST", "TESTS"]:
                if (self.root / i).exists():
                    self._tests = self.root / i
                    return self._tests

            raise RuntimeError(mylogging.format_str("Test path not found."))

        return self._tests

    @tests.setter
    def tests(self, new_path: PathLike) -> None:
        self._tests = validate_path(new_path)

    @property
    def docs(self) -> Path:
        """Where documentation is stored. Usually root / docs.

        'doc', 'Doc', 'Docs', 'DOC', 'DOCS' also inferred if on root.

        Type:
            Path

        Default:
            root_path/docs
        """
        if not self._docs:
            for i in ["docs", "doc", "Doc", "Docs", "DOC", "DOCS"]:
                if (self.root / i).exists():
                    self._docs = self.root / i
                    return self._docs

            raise RuntimeError(mylogging.format_str("Test path not found."))

        return self._docs

    @docs.setter
    def docs(self, new_path: PathLike) -> None:
        self._docs = validate_path(new_path)

    @property
    def readme(self) -> Path:
        """Return README path whether it's capitalized or not

        'Readme.md', 'readme.md', and rst extension also inferred if on root.

        Type:
            Path

        Default:
            root_path/README.md
        """
        if not self._readme:
            for i in ["README.md", "Readme.md", "readme.md", "README.rst", "Readme.rst", "readme.rst"]:
                if (self.root / i).exists():
                    self._readme = self.root / i
                    return self._readme
            raise RuntimeError(mylogging.format_str("Readme path not found."))

        return self._readme

    @readme.setter
    def readme(self, new_path: PathLike) -> None:
        self._readme = validate_path(new_path)

    def reset_paths(self):
        """Reset all the paths to default."""
        self._root = None
        self._app = None
        self._init = None
        self._tests = None
        self._docs = None
        self._readme = None


PROJECT_PATHS = _ProjectPaths()


def find_path(
    name: str,
    folder: PathLike | None = None,
    exclude_names: Sequence[str] = ("node_modules", "build", "dist"),
    exclude_paths: Sequence[PathLike] = (),
    levels: int = 5,
) -> Path:
    """Search for file or folder in defined folder (cwd() by default) and return it's path.

    Args:
        name (str): Name of folder or file that should be found. If using file, use it with extension
            e.g. "app.py".
        folder (PathLike | None, optional): Where to search. If None, then root is used (cwd by default).
            Defaults to None.
        exclude_names (Sequence[str], optional): List or tuple of ignored names. If this name is whenever in
            path, it will be ignored. Defaults to ('node_modules', 'build', 'dist').
        exclude_paths (Sequence[PathLike], optional): List or tuple of ignored paths. If defined path is
            subpath of found file, it will be ignored. If relative, it has to be from cwd. Defaults to ().
        levels (str, optional): Recursive number of analyzed folders. Defaults to 5.

    Returns:
        Path: Found path.

    Raises:
        FileNotFoundError: If file is not found.
    """
    validate_sequence(exclude_names, "exclude_names")
    validate_sequence(exclude_paths, "exclude_paths")

    folder = PROJECT_PATHS.root if not folder else validate_path(folder)

    for lev in range(levels):
        glob_file_str = f"{'*/' * lev}{name}"

        for i in folder.glob(glob_file_str):
            is_wanted_file = True
            for j in exclude_names:
                if j in i.parts:
                    is_wanted_file = False
                    break

            if is_wanted_file:
                for j in exclude_paths:
                    excluded_name = Path(j).resolve()
                    if i.as_posix().startswith(excluded_name.as_posix()):
                        is_wanted_file = False
                        break

            if is_wanted_file:
                return i

    # If not returned - not found
    raise FileNotFoundError(mylogging.format_str(f"File `{name}` not found"))


def get_desktop_path() -> Path:
    """Get desktop path.

    Returns:
        Path: Return pathlib Path object. If you want string, use `.as_posix()`

    Example:
        >>> desktop_path = get_desktop_path()
        >>> desktop_path.exists() and "Desktop" in desktop_path.as_posix()
        True
    """
    return Path.home() / "Desktop"


def validate_path(path: PathLike) -> Path:
    """Convert to pathlib path, resolve to full path and check if exists.

    Args:
        path (PathLike): Validated path.

    Raises:
        FileNotFoundError: If file do not exists.

    Returns:
        Path: Pathlib Path object.

    Example:
        >>> from pathlib import Path
        >>> existing_path = validate_path(Path.cwd())
        >>> non_existing_path = validate_path("not_existing")
        Traceback (most recent call last):
        FileNotFoundError: ...
    """
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(mylogging.format_str(f"File nor folder found on defined path {path}"))
    return path
