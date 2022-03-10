"""Tests for cicd module."""

# pylint: disable=missing-function-docstring


from __future__ import annotations
import shutil
from pathlib import Path
import sys
import os

root_path = Path(__file__).parents[1].as_posix()  # pylint: disable=no-member
sys.path.insert(0, root_path)


from mypythontools import cicd
from mypythontools.helpers.paths import PROJECT_PATHS

test_project_path = Path("tests").resolve() / "tested project"
# test_project_venv = test_project_path / "venv/310"
# requirements = Path("requirements.txt").resolve()


def test_docs_regenerate():
    rst_path = test_project_path / "docs" / "source" / "project_lib.rst"
    another_rst_path = test_project_path / "docs" / "source" / "content" / "also_not_deleted.rst"
    not_deleted = test_project_path / "docs" / "source" / "not_deleted.rst"

    if rst_path.exists():
        rst_path.unlink()  # missing_ok=True from python 3.8 on...

    if not not_deleted.exists():
        with open(not_deleted, "w") as not_deleted_file:
            not_deleted_file.write("I will not be deleted.")
            # missing_ok=True from python 3.8 on...

    cicd.project_utils.project_utils_functions.docs_regenerate(
        keep=("conf.py", "index.rst", "_static", "_templates", "content/**", "not_deleted.rst")
    )

    assert rst_path.exists()
    assert another_rst_path.exists()
    assert not_deleted.exists()


def test_reformat_with_black():
    cicd.project_utils.project_utils_functions.reformat_with_black()


def test_set_version():
    cicd.project_utils.project_utils_functions.set_version("0.0.2")
    assert cicd.project_utils.project_utils_functions.get_version() == "0.0.2"
    cicd.project_utils.project_utils_functions.set_version("0.0.1")


def test_build():

    # Build app with pyinstaller example
    cicd.build.build_app(
        main_file="app.py",
        console=True,
        debug=True,
        clean=False,
        build_web=False,
        ignored_packages=["matplotlib"],
        virtualenv=sys.prefix,
        sync_requirements=None,
    )

    assert (test_project_path / "dist").exists()

    shutil.rmtree(test_project_path / "build")
    shutil.rmtree(test_project_path / "dist")


def test_add_readme_tests():
    for i in PROJECT_PATHS.tests.glob("*"):
        if i.name.startswith("test_readme_generated"):
            i.unlink()

    cicd.tests.add_readme_tests()
    for i in PROJECT_PATHS.tests.glob("*"):
        if i.name.startswith("test_readme_generated"):
            print("Readme tests found.")


def test_project_utils_pipeline():
    cicd.project_utils.project_utils_pipeline(
        commit_and_push_git=False,
        deploy=False,
        allowed_branches=None,
        test_options={"virtualenvs": [sys.prefix], "sync_requirements": None},
    )


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    cicd.tests.setup_tests()

    test_project_path = Path("tests").resolve() / "tested project"
    os.chdir(test_project_path)

    # test_cicd()
    # test_build()

    import platform
    from mypythontools.cicd.venvs import Venv
    from pathlib import Path

    path = "venv/310" if platform.system() == "Windows" else "venv/ubuntu"
    venv = Venv(path)
    venv.create()  # If already exists, it's skipped
    venv.install_library("colorama==0.3.9")
    "colorama==0.3.9" in venv.list_packages()
    # tru
    venv.sync_requirements()  # There ia a 8.0.3 in requirements.txt
    "colorama==0.4.4" in venv.list_packages()

    # tru
    venv.remove()
    Path(path).exists()
    # false
