"""Module with functions for 'tests' subpackage."""

from __future__ import annotations
import subprocess
from pathlib import Path
import sys
import warnings

from typing_extensions import Literal
import numpy as np

import mylogging

from ...helpers.paths import PROJECT_PATHS, validate_path
from ..venvs import venvs
from ...helpers.misc import misc


def setup_tests(
    generate_readme_tests: bool = True,
    matplotlib_test_backend: bool = False,
    set_numpy_random_seed: int | None = 2,
) -> None:
    """Add paths to be able to import local version of library as well as other test files.

    Value Mylogging.config.colorize = 0 changed globally.

    Note:
        Function expect `tests` folder on root. If not, test folder will not be added to sys path and
        imports from tests will not work.

    Args:
        generate_readme_tests (bool, optional): If True, generete new tests from readme if there are
            new changes. Defaults to True.
        matplotlib_test_backend (bool, optional): If using matlplotlib, it need to be
            closed to continue tests. Change backend to agg. Defaults to False.
        set_numpy_random_seed (int | None): If using numpy random numbers, it will be each time the same.
            Defaults to 2.

    """
    mylogging.config.colorize = False

    PROJECT_PATHS.add_root_to_sys_path()

    # Find paths and add to sys.path to be able to import local modules
    test_dir_path = PROJECT_PATHS.tests

    if test_dir_path.as_posix() not in sys.path:
        sys.path.insert(0, test_dir_path.as_posix())

    if matplotlib_test_backend:
        import matplotlib

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            matplotlib.use("agg")

    if generate_readme_tests:
        add_readme_tests()

    if set_numpy_random_seed:
        np.random.seed(2)


def run_tests(
    tested_path: None | str | Path = None,
    tests_path: None | str | Path = None,
    test_coverage: bool = True,
    stop_on_first_error: bool = True,
    use_virutalenv: bool = True,
    remove_venv: bool = False,
    requirements: str | Path | list[str] | list[Path] = "infer",
    verbose: Literal[0, 1, 2] = 1,
    extra_args: None | list = None,
) -> None:
    """Run tests. If any test fails, raise an error.

    Args:
        tested_path (str | Path, optional): If None, root is used. root is necessary if using doctests
            'Tests' folder not works for doctests in modules. Defaults to None.
        tests_path (str | Path, optional): If None, tests is used. It means where venv will be stored etc.
            Defaults to None.
        test_coverage (bool, optional): Whether run test coverage plugin. If True, pytest-cov must
            be installed. Defaults to True.
        stop_on_first_error (bool, optional): Whether stop on first error. Defaults to True.
        use_virutalenv (bool, optional): Whether run new virtualenv and install all libraries from
            requirements.txt. Defaults to True.
        remove_venv (bool, optional): Whether remove created venv. It's usually not necessary, because
            packages not in requirements are updated. Defaults to True
        requirements (str | Path | list[str] | list[Path], optional): If using `use_virutalenv`
            define what libraries will be installed by path to requirements.txt. Can also be a list of more
            files e.g `["requirements.txt", "requirements_dev.txt"]`. If "infer", autodetected (all
            requirements). Defaults to "infer".
        verbose (Literal[0, 1, 2], optional): Whether print details on errors or keep silent. If 0, no
            details, parameters `-q and `--tb=no` are added. if 1, some details are added --tb=short. If 2,
            more details are printed (default --tb=auto) Defaults to 1.
        extra_args (None | list, optional): List of args passed to pytest. Defaults to None

    Raises:
        Exception: If any test fail, it will raise exception (git hook do not continue...).

    Note:
        By default args to quiet mode and no traceback are passed. Usually this just runs automatic tests.
        If some of them fail, it's further analyzed in some other tool in IDE.

    Example:

        ::

            run_tests(verbose=2)
    """
    tested_path = validate_path(tested_path) if tested_path else PROJECT_PATHS.root
    tests_path = validate_path(tests_path) if tests_path else PROJECT_PATHS.tests
    tested_path_str = misc.get_console_str_with_quotes(tested_path)

    if not extra_args:
        extra_args = []

    if not test_coverage:
        pytest_args = [tested_path_str]
    else:
        pytest_args = [
            tested_path_str,
            "--cov",
            misc.get_console_str_with_quotes(PROJECT_PATHS.app),
            "--cov-report",
            "xml:.coverage.xml",
        ]

    if stop_on_first_error:
        extra_args.append("-x")

    if verbose == 0:
        extra_args.append("-q")
        extra_args.append("--tb=no")
    elif verbose == 1:
        extra_args.append("--tb=short")

    complete_args = [
        "pytest",
        *pytest_args,
        *extra_args,
    ]

    test_command = " ".join(complete_args)

    if use_virutalenv:
        my_venv = venvs.Venv(PROJECT_PATHS.root / "venv")
        my_venv.create()
        my_venv.sync_requirements(requirements)

        test_command = f"{my_venv.activate_command} && {test_command}"

    try:
        pytested = subprocess.run(  # pylint: disable=subprocess-run-check
            test_command, cwd=tested_path.as_posix(), capture_output=True
        )  # , shell=True
    except Exception:
        mylogging.traceback(
            "Tests failed and did not run. Try this command in terminal to know why it failed."
            f"\n\n{test_command}\n\n"
        )
        raise

    if test_coverage and Path(".coverage").exists():
        Path(".coverage").unlink()

    if use_virutalenv and remove_venv:
        my_venv.remove()  # type: ignore

    if pytested.returncode != 0:
        raise RuntimeError(
            mylogging.format_str(
                f"Pytest failed. Used command is\n\n{test_command}\n\n"
                f"Stdout:\n\n{pytested.stdout}\n\n"
                f"Stderr:\n\n{pytested.stderr}\n\n"
            )
        )


def add_readme_tests(
    readme_path: None | str | Path = None, test_folder_path: None | str | Path = None
) -> None:
    """Generate pytest tests script file from README.md and save it to tests folder. Can be called
    from conftest.

    Args:
        readme_path (None | str | Path, optional): If None, autodetected (README.md, Readme.md or readme.md
            on root). Defaults to None.
        test_folder_path (None | str | Path, optional): If None, autodetected (if root / tests).
            Defaults to None.

    Raises:
        FileNotFoundError: If Readme not found.

    Example:
        >>> for i in PROJECT_PATHS.tests.glob("*"):
        ...     if i.name.startswith("test_readme_generated"):
        ...         i.unlink()
        ...
        >>> add_readme_tests()
        >>> for i in PROJECT_PATHS.tests.glob("*"):
        ...     if i.name.startswith("test_readme_generated"):
        ...         print("Readme tests found.")
        Readme tests found.

    Note:
        Only blocks with python defined syntax will be evaluated. Example:

            ```python
            import numpy
            ```

        If you want to import modules and use some global variables, add `<!--phmdoctest-setup-->` directive
        before block with setup code.
        If you want to skip some test, add `<!--phmdoctest-mark.skip-->`
    """

    readme_path = validate_path(readme_path) if readme_path else PROJECT_PATHS.readme
    test_folder_path = validate_path(test_folder_path) if test_folder_path else PROJECT_PATHS.tests

    readme_date_modified = str(readme_path.stat().st_mtime).split(".", maxsplit=1)[0]  # Keep only seconds
    readme_tests_name = f"test_readme_generated-{readme_date_modified}.py"

    test_file_path = test_folder_path / readme_tests_name

    # File not changed from last tests
    if test_file_path.exists():
        return

    for i in test_folder_path.glob("*"):
        if i.name.startswith("test_readme_generated"):
            i.unlink()

    generate_readme_test_command = [
        "phmdoctest",
        readme_path.as_posix(),
        "--outfile",
        test_file_path.as_posix(),
    ]

    readme_tests = subprocess.run(generate_readme_test_command)  # pylint: disable=subprocess-run-check

    if readme_tests.returncode != 0:
        raise RuntimeError(
            mylogging.format_str(
                f"Readme test creation failed with error code {readme_tests.returncode}. Try "
                "\n\n{generate_readme_test_command}\n\n in on your root."
            )
        )


def deactivate_test_settings() -> None:
    """Sometimess you want to run test just in normal mode (enable plots etc.). Usually at the end of
    test file in `if __name__ = "__main__":` block."""
    mylogging.config.colorize = True

    if "matplotlib" in sys.modules:

        import matplotlib
        from importlib import reload

        reload(matplotlib)
