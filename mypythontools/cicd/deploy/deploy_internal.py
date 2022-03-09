"""Module with functions for 'deploy' subpackage."""

from __future__ import annotations
import os
import shutil

import mylogging

from ...helpers.paths import PROJECT_PATHS, validate_path, PathLike
from ...helpers.misc import (
    terminal_do_command,
    check_script_is_available,
    check_library_is_available,
)


def deploy_to_pypi(setup_path: None | PathLike = None, clean: bool = True, verbose: bool = True) -> None:
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
        verbose (bool, optional): If True, result of terminal command will be printed to console.
            Defaults to False.
    """
    usr = os.environ.get("TWINE_USERNAME")
    password = os.environ.get("TWINE_PASSWORD")

    if not usr or not password:
        raise KeyError(
            mylogging.format_str("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")
        )

    check_library_is_available("build", "build")
    check_script_is_available("twine", "twine")

    setup_path = PROJECT_PATHS.root / "setup.py" if not setup_path else validate_path(setup_path)

    setup_dir_path = setup_path.parent

    dist_path = setup_dir_path / "dist"
    build_path = setup_dir_path / "build"

    if dist_path.exists():
        shutil.rmtree(dist_path)

    if build_path.exists():
        shutil.rmtree(build_path)

    build_command = f"pyproject-build"

    terminal_do_command(
        build_command,
        cwd=setup_dir_path.as_posix(),
        verbose=verbose,
        error_header="Library build necessary for deploying to PyPi failed.",
    )

    command = f"twine upload -u {usr} -p {password} dist/*"

    terminal_do_command(
        command,
        cwd=setup_dir_path.as_posix(),
        verbose=verbose,
        error_header="Deploying to PyPi failed.",
    )

    if clean:
        shutil.rmtree(dist_path, ignore_errors=True)
        shutil.rmtree(build_path, ignore_errors=True)
