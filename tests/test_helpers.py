"""Tests for helpers module."""

# pylint: disable=missing-function-docstring

from pathlib import Path
import sys

root_path = Path(__file__).parents[1].as_posix()  # pylint: disable=no-member
sys.path.insert(0, root_path)


from mypythontools import helpers
from mypythontools import cicd

test_project_path = Path("tests").resolve() / "tested_project"


def test_paths():

    assert helpers.paths.PROJECT_PATHS.root == test_project_path
    assert helpers.paths.PROJECT_PATHS.init == test_project_path / "project_lib" / "__init__.py"
    assert helpers.paths.PROJECT_PATHS.app == test_project_path / "project_lib"
    assert helpers.paths.PROJECT_PATHS.docs == test_project_path / "docs"
    assert helpers.paths.PROJECT_PATHS.readme == test_project_path / "README.md"
    assert helpers.paths.PROJECT_PATHS.tests == test_project_path / "tests"


def test_config_argparse():
    """Doctest not tested in config. If changing test, change docs as well."""

    import subprocess

    options = [
        # {"name": "bool_arg", "input_value": "True", "expected_value": "True", "type": "bool"},
        # {"name": "int_arg", "input_value": "666", "expected_value": "666", "type": "int"},
        # {"name": "float_arg", "input_value": "666", "expected_value": "666", "type": "float"},
        # {"name": "str_arg", "input_value": "666", "expected_value": "666", "type": "str"},
        # {"name": "list_arg", "input_value": "[666]", "expected_value": "666", "type": "list"},
        # {"name": "dict_arg", "input_value": "\"{'key': 666}\"", "expected_value": "666", "type": "dict"},
    ]

    for i in options:

        output = subprocess.check_output(
            f"python tests/helpers/argparse_config.py --{i['name']} {i['input_value']}",
            cwd=root_path,
            text=True,
        ).strip()

        assert all(member in output for member in [i["name"], i["expected_value"], i["type"]])

    get_help = subprocess.check_output(
        "python tests/helpers/argparse_config.py --help", cwd=root_path, text=True
    ).strip()

    is_error = False

    try:
        subprocess.check_output(
            "python tests/helpers/argparse_config.py --bool_arg", cwd=root_path, text=True
        ).strip()
    except Exception:
        is_error = True

    assert is_error, "Value not parsed with correct type, but error not raised"

    is_error = False

    try:
        subprocess.check_output(
            "python tests/helpers/argparse_config.py --nonexisting_arg nonsense", cwd=root_path, text=True
        ).strip()
    except Exception:
        is_error = True
    assert is_error, "Non existing variable passed"

    assert "This should be in CLI help" in get_help and "How it works." in get_help


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    cicd.tests.setup_tests()

    test_config_argparse()
