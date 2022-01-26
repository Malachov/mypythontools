"""Module with functions for 'deploy' subpackage."""

from __future__ import annotations
import subprocess
import os
import shutil
from pathlib import Path
import platform

import mylogging

from ...helpers import paths


def deploy_to_pypi(setup_path: None | str | Path = None) -> None:
    """Publish python library to PyPi. Username and password are set
    with env vars `TWINE_USERNAME` and `TWINE_PASSWORD`.

    Note:
        You need working `setup.py` file. If you want to see example, try the one from project-starter on

        https://github.com/Malachov/mypythontools/blob/master/content/project-starter/setup.py

    Args:
        setup_path(None | str | Path, optional): Function suppose, that there is a setup.py somewhere in cwd.
            If not, path will be inferred. Build and dist folders will be created in same directory.
            Defaults to None.
    """

    usr = os.environ.get("TWINE_USERNAME")
    pas = os.environ.get("TWINE_PASSWORD")

    if not usr or not pas:
        raise KeyError(
            mylogging.format_str("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")
        )

    setup_path = paths.PROJECT_PATHS.root / "setup.py" if not setup_path else paths.validate_path(setup_path)

    setup_dir_path = setup_path.parent

    dist_path = setup_dir_path / "dist"
    build_path = setup_dir_path / "build"

    if dist_path.exists():
        shutil.rmtree(dist_path)

    if build_path.exists():
        shutil.rmtree(build_path)

    if platform.system() == "Windows":
        python_command = "python"
    else:
        python_command = "python3"

    build_command = f"{python_command} setup.py sdist bdist_wheel"

    try:
        subprocess.run(
            build_command.split(),
            cwd=setup_dir_path.as_posix(),
            check=True,
        )
    except Exception:
        mylogging.traceback(
            f"Library build with pyinstaller failed. Try \n\n{build_command}\n\n in folder {setup_dir_path}."
        )
        raise

    command_list = [
        "twine",
        "upload",
        "-u",
        os.environ["TWINE_USERNAME"],
        "-p",
        os.environ["TWINE_PASSWORD"],
        "dist/*",
    ]

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

    shutil.rmtree(dist_path)
    shutil.rmtree(build_path)
