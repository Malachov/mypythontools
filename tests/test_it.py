#%%
import shutil
from pathlib import Path
import sys
import os

sys.path.insert(0, Path(__file__).parents[1].as_posix())

import mypythontools

test_project_path = Path("tests").resolve() / "tested_project"


def test_paths():

    assert mypythontools.paths.PROJECT_PATHS.ROOT_PATH == test_project_path
    assert mypythontools.paths.PROJECT_PATHS.INIT_PATH == test_project_path / "project_lib" / "__init__.py"
    assert mypythontools.paths.PROJECT_PATHS.APP_PATH == test_project_path / "project_lib"
    assert mypythontools.paths.PROJECT_PATHS.DOCS_PATH == test_project_path / "docs"
    assert mypythontools.paths.PROJECT_PATHS.README_PATH == test_project_path / "README.md"
    assert mypythontools.paths.PROJECT_PATHS.TEST_PATH == test_project_path / "tests"


def test_utils():

    rst_path = test_project_path / "docs" / "source" / "project_lib.rst"
    not_deleted = test_project_path / "docs" / "source" / "not_deleted.rst"

    if rst_path.exists():
        rst_path.unlink()  # missing_ok=True from python 3.8 on...

    mypythontools.utils.sphinx_docs_regenerate(exclude_paths=["not_deleted.rst"])

    mypythontools.utils.reformat_with_black()

    assert rst_path.exists()
    assert not_deleted.exists()

    mypythontools.utils.set_version("0.0.2")
    assert mypythontools.utils.get_version() == "0.0.2"
    mypythontools.utils.set_version("0.0.1")

    # TODO test if correct


def test_build():

    # Build app with pyinstaller example
    mypythontools.build.build_app(
        main_file="app.py",
        console=True,
        debug=True,
        cleanit=False,
        build_web=False,
    )

    assert (test_project_path / "dist").exists()

    shutil.rmtree(test_project_path / "build")
    shutil.rmtree(test_project_path / "dist")


if __name__ == "__main__":
    # Find paths and add to sys.path to be able to import local modules
    mypythontools.tests.setup_tests()

    test_project_path = Path("tests").resolve() / "tested_project"
    os.chdir(test_project_path)
    mypythontools.paths.PROJECT_PATHS = mypythontools.paths._ProjectPaths()

    # test_it()
