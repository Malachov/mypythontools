"""Module with functions around testing. You can run tests including doctest with generating coverage,
you can generate tests from readme or you can configure tests in conftest with single call."""

from __future__ import annotations
import subprocess
from pathlib import Path
import sys
import warnings

from typing_extensions import Literal
import mylogging

from .paths import PROJECT_PATHS, validate_path
from . import venvs
from . import misc


def setup_tests(
    generate_readme_tests: bool = True,
    matplotlib_test_backend: bool = False,
) -> None:
    """Add paths to be able to import local version of library as well as other test files.

    Value Mylogging.config.COLORIZE = 0 changed globally.

    Note:
        Function expect `tests` folder on root. If not, test folder will not be added to sys path and
        imports from tests will not work.

    Args:
        generate_readme_tests (bool, optional): If True, generete new tests from readme if there are new changes.
            Defaults to True.
        matplotlib_test_backend (bool, optional): If using matlplotlib, it need to be
            closed to continue tests. Change backend to agg. Defaults to False.
    """
    mylogging.config.COLORIZE = False

    PROJECT_PATHS.add_ROOT_PATH_to_sys_path()

    # Find paths and add to sys.path to be able to import local modules
    test_dir_path = PROJECT_PATHS.TEST_PATH

    if test_dir_path.as_posix() not in sys.path:
        sys.path.insert(0, test_dir_path.as_posix())

    if matplotlib_test_backend:
        import matplotlib

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            matplotlib.use("agg")

    if generate_readme_tests:
        add_readme_tests()


def run_tests(
    tested_path: str | Path = "infer",
    tests_path: str | Path = "infer",
    test_coverage: bool = True,
    stop_on_first_error: bool = True,
    use_virutalenv: bool = True,
    remove_venv: bool = False,
    requirements: list | str | Path = "infer",
    verbose: Literal[0, 1, 2] = 1,
    extra_args: list = [],
) -> None:
    """Run tests. If any test fails, raise an error.

    Args:
        tested_path (str | Path, optional): If "infer", ROOT_PATH is used. ROOT_PATH is necessary if using doctests
            'Tests' folder not works for doctests in modules. Defaults to None.
        tests_path (str | Path, optional): If "infer", TEST_PATH is used. It means where venv will be stored etc. Defaults to "infer".
        test_coverage (bool, optional): Whether run test coverage plugin. If True, pytest-cov must be installed. Defaults to True.
        stop_on_first_error (bool, optional): Whether stop on first error. Defaults to True.
        use_virutalenv (bool, optional): Whether run new virtualenv and install all libraries from requirements.txt. Defaults to True.
        remove_venv (bool, optional): Whether remove created venv. It's usually not necessary, because packages not in requirements are updated. Defaults to True
        requirements (list | str | Path, optional): If using `use_virutalenv` define what libraries will be installed by path to requirements.txt.
           Can also be a list of more files e.g `["requirements.txt", "requirements_dev.txt"]`. If "infer", autodetected (all requirements). Defaults to "infer".
        verbose (Literal[0, 1, 2], optional): Whether print detailes on errors or keep silent. If 0, no details, parameters `-q and `--tb=no` are added.
            if 1, some details are added --tb=short. If 2, more details are printed (default --tb=auto)
            Defaults to 1.
        extra_args (list, optional): List of args passed to pytest. Defaults to []

    Raises:
        Exception: If any test fail, it will raise exception (git hook do not continue...).

    Note:
        By default args to quiet mode and no traceback are passed. Usually this just runs automatic tests. If some of them fail,
        it's further analyzed in some other tool in IDE.

    Example:
        >>> run_tests()
    """
    tested_path = PROJECT_PATHS.ROOT_PATH if tested_path == "infer" else validate_path(tested_path)
    tests_path = PROJECT_PATHS.TEST_PATH if tests_path == "infer" else validate_path(tests_path)
    tested_path_str = misc.get_console_str_with_quotes(tested_path)

    if not test_coverage:
        pytest_args = [tested_path_str]
    else:
        pytest_args = [
            tested_path_str,
            "--cov",
            misc.get_console_str_with_quotes(PROJECT_PATHS.APP_PATH),
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
        my_venv = venvs.MyVenv(PROJECT_PATHS.ROOT_PATH / "venv")
        my_venv.create()
        my_venv.sync_requirements(requirements)

        test_command = f"{my_venv.activate_command} && {test_command}"

    try:
        pytested = subprocess.run(test_command, cwd=tested_path.as_posix())  # , shell=True
    except Exception:
        mylogging.traceback(
            f"Tests failed and did not run. Try this command in terminal to know why it failed.\n{test_command}"
        )
        raise

    if test_coverage and Path(".coverage").exists():
        Path(".coverage").unlink()

    if use_virutalenv and remove_venv:
        my_venv.remove()

    if pytested.returncode != 0:
        raise RuntimeError(mylogging.return_str("Pytest failed"))


def add_readme_tests(readme_path: str | Path = "infer", test_folder_path: str | Path = "infer") -> None:
    """Generate pytest tests script file from README.md and save it to tests folder. Can be called from conftest.

    Args:
        readme_path (str | Path, optional): If 'infer', autodetected (README.md, Readme.md or readme.md on root).
            Defaults to 'infer'.
        test_folder_path (str | Path, optional): If 'infer', autodetected (if ROOT_PATH / tests). Defaults to 'infer.

    Raises:
        FileNotFoundError: If Readme not found.

    Example:
        >>> for i in PROJECT_PATHS.TEST_PATH.glob("*"):
        ...     if i.name.startswith("test_readme_generated"):
        ...         i.unlink()
        ...
        >>> add_readme_tests()
        >>> for i in PROJECT_PATHS.TEST_PATH.glob("*"):
        ...     if i.name.startswith("test_readme_generated"):
        ...         print("Readme tests found.")
        Readme tests found.

    Note:
        Only blocks with python defined syntax will be evaluated. Example:

            ```python
            import numpy
            ```

        If you want to import modules and use some global variables, add `<!--phmdoctest-setup-->` this directive above
        block with setup code.
        If you want to skip some test, add `<!--phmdoctest-mark.skip-->`
    """

    readme_path = PROJECT_PATHS.README_PATH if readme_path == "infer" else validate_path(readme_path)
    test_folder_path = (
        PROJECT_PATHS.TEST_PATH if test_folder_path == "infer" else validate_path(test_folder_path)
    )

    readme_date_modified = str(readme_path.stat().st_mtime).split(".")[0]  # Keep only seconds
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
    try:
        subprocess.run(generate_readme_test_command)
    except Exception:
        mylogging.traceback(
            f"Readme test creation failed. Try \n\n{generate_readme_test_command}\n\n in on your root."
        )
        raise


def deactivate_test_settings() -> None:
    """Sometimes you want to run test just in normal mode (enable plots etc.). Usually at the end of test file in `if __name__ = "__main__":` block."""
    mylogging.config.COLORIZE = True

    if "matplotlib" in sys.modules:

        import matplotlib
        from importlib import reload

        reload(matplotlib)
