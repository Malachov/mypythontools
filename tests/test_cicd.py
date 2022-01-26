"""Tests for cicd module."""

# pylint: disable=missing-function-docstring

import shutil
from pathlib import Path
import sys
import os

root_path = Path(__file__).parents[1].as_posix()  # pylint: disable=no-member
sys.path.insert(0, root_path)

from mypythontools import cicd

test_project_path = Path("tests").resolve() / "tested_project"


def test_cicd():
    rst_path = test_project_path / "docs" / "source" / "project_lib.rst"
    not_deleted = test_project_path / "docs" / "source" / "not_deleted.rst"

    if rst_path.exists():
        rst_path.unlink()  # missing_ok=True from python 3.8 on...

    if not not_deleted.exists():
        with open(not_deleted, "w") as not_deleted_file:
            not_deleted_file.write("I will not be deleted.")
            # missing_ok=True from python 3.8 on...

    cicd.project_utils.project_utils_functions.sphinx_docs_regenerate(exclude_paths=["not_deleted.rst"])

    cicd.project_utils.project_utils_functions.reformat_with_black()

    assert rst_path.exists()
    assert not_deleted.exists()

    cicd.project_utils.project_utils_functions.set_version("0.0.2")
    assert cicd.project_utils.project_utils_functions.get_version() == "0.0.2"
    cicd.project_utils.project_utils_functions.set_version("0.0.1")

    # TODO test if correct


def test_build():

    # Build app with pyinstaller example
    cicd.build.build_app(
        main_file="app.py",
        console=True,
        debug=True,
        clean=False,
        build_web=False,
        ignored_packages=["matplotlib"],
    )

    assert (test_project_path / "dist").exists()

    shutil.rmtree(test_project_path / "build")
    shutil.rmtree(test_project_path / "dist")


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    cicd.tests.setup_tests()

    test_project_path = Path("tests").resolve() / "tested_project"
    os.chdir(test_project_path)

    # test_cicd()
    # test_build()
