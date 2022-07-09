"""Tests for helpers module."""

from __future__ import annotations
from pathlib import Path
import sys
import subprocess
import os

root_path = Path(__file__).parents[1].as_posix()  # pylint: disable=no-member
sys.path.insert(0, root_path)

# from mypythontools_cicd.tests import setup_tests

import mypythontools
from mypythontools.system import get_console_str_with_quotes, PYTHON

# pylint: disable=missing-function-docstring

# setup_tests()

tests_path = Path("tests").resolve()
test_project_path = tests_path / "tested project"

# pylint: disable=missing-function-docstring,


def test_config_argparse():
    """Doctest not tested in config. If changing test, change docs as well."""

    options = [
        {"name": "none_arg", "input_value": "None", "expected_value": "None", "type": type(None)},
        {"name": "bool_arg", "input_value": "True", "expected_value": "True", "type": "bool"},
        {"name": "int_arg", "input_value": "666", "expected_value": "666", "type": "int"},
        {"name": "float_arg", "input_value": "666", "expected_value": "666", "type": "float"},
        {"name": "str_arg", "input_value": "666", "expected_value": "666", "type": "str"},
        {"name": "list_arg", "input_value": '"[666, 777]"', "expected_value": "666", "type": "list"},
        {
            "name": "dict_arg",
            "input_value": "\"{'key': 666, 'key2': 777}\"",
            "expected_value": "666",
            "type": "dict",
        },
    ]

    argparse_script_path = get_console_str_with_quotes(tests_path / "helpers" / "argparse_config.py")

    for i in options:
        output = subprocess.check_output(
            f"{PYTHON} {argparse_script_path} --{i['name']} {i['input_value']}",
            cwd=root_path,
            text=True,
            shell=True,
        ).strip()

        assert all(member in output for member in [i["name"], i["expected_value"], str(i["type"])])

    get_help = subprocess.check_output(
        f"{PYTHON} {argparse_script_path} --help", cwd=root_path, text=True, shell=True
    ).strip()

    assert "This should be in CLI help" in get_help and "How it works." in get_help

    is_error = False

    try:
        subprocess.check_output(
            f"{PYTHON} {argparse_script_path} --bool_arg", cwd=root_path, text=True, shell=True
        ).strip()
    except Exception:
        is_error = True

    assert is_error, "Value not parsed with correct type, but error not raised"

    is_error = False

    try:
        subprocess.check_output(
            f"{PYTHON} {argparse_script_path} --nonexisting_arg nonsense",
            cwd=root_path,
            text=True,
            shell=True,
        ).strip()
    except Exception:
        is_error = True
    assert is_error, "Non existing variable passed"


def test_delete_files():
    dir_path = Path("dir_to_be_deleted")

    file_in_folder = dir_path / "to_be_deleted.txt"
    file_one = Path("to_be_deleted_one.txt")
    file_two = Path("to_be_deleted_two.txt")

    os.mkdir(dir_path.as_posix())

    for i in [file_in_folder, file_one, file_two]:
        with open(i, "w") as opened_file:
            opened_file.write("content")
        assert i.exists, f"File {i} was not created."

    mypythontools.misc.delete_files(dir_path)
    mypythontools.misc.delete_files([file_one, file_two.as_posix()])

    assert not dir_path.exists(), "Directory was not deleted."
    assert not (file_one.exists() and file_two.exists()), "Directory was not deleted."


if __name__ == "__main__":

    pass
