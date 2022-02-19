"""Module with functions for 'deploy' subpackage."""

from __future__ import annotations
import subprocess
import os
import shutil
import platform
import sys

import mylogging

from ...helpers.paths import PROJECT_PATHS, validate_path, PathLike
from ...helpers.misc import get_console_str_with_quotes
from ...cicd.venvs import Venv


def deploy_to_pypi(setup_path: None | PathLike = None, clean: bool = True) -> None:
    """Publish python library to PyPi.

    Username and password are set with env vars `TWINE_USERNAME` and `TWINE_PASSWORD`.

    Note:
        You need working `setup.py` file. If you want to see example, try the one from project-starter on

        https://github.com/Malachov/mypythontools/blob/master/content/project-starter/setup.py

    Args:
        setup_path (None | PathLike, optional): Function suppose, that there is a setup.py somewhere in cwd.
            If not, path will be inferred. Build and dist folders will be created in same directory.
            Defaults to None.
        clean (bool, optional): Whether delete created build and dist folders.
    """
    usr = os.environ.get("TWINE_USERNAME")
    password = os.environ.get("TWINE_PASSWORD")

    if not usr or not password:
        raise KeyError(
            mylogging.format_str("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")
        )

    setup_path = PROJECT_PATHS.root / "setup.py" if not setup_path else validate_path(setup_path)

    setup_dir_path = setup_path.parent

    dist_path = setup_dir_path / "dist"
    build_path = setup_dir_path / "build"

    if dist_path.exists():
        shutil.rmtree(dist_path)

    if build_path.exists():
        shutil.rmtree(build_path)

    py_executable = get_console_str_with_quotes(sys.executable)

    python_command = f"{py_executable} -m " if platform.system() == "Windows" else f"{py_executable} -m "

    build_command = f"{python_command} build"

    print("\n\n", py_executable, "\n\n")

    try:
        result = subprocess.run(build_command, cwd=setup_dir_path.as_posix(), check=True)
        if result.returncode != 0:
            raise RuntimeError
    except Exception:
        mylogging.traceback(
            f"Library packaging failed. Try \n\n{build_command}\n\n in folder {setup_dir_path}."
        )
        raise

    command_list = f"{py_executable} -m twine upload -u {usr} -p {password} dist/*"

    try:
        subprocess.run(
            command_list,
            cwd=setup_dir_path.as_posix(),
            check=True,
        )
    except Exception:
        mylogging.traceback(
            f"Deploying on PyPi failed. Try \n\n\t{' '.join(command_list)}\n\n in folder {setup_dir_path}."
        )
        raise

    if clean:
        shutil.rmtree(dist_path, ignore_errors=True)
        shutil.rmtree(build_path, ignore_errors=True)
