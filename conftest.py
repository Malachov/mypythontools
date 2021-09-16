import os
import inspect
from pathlib import Path
import sys
import pytest

# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
ROOT_PATH = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parent

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH.as_posix())

import mypythontools

mypythontools.tests.setup_tests()


@pytest.fixture(autouse=True)
def setup_tests():

    cwd_backup = Path.cwd()

    test_project_path = Path("tests").resolve() / "tested_project"
    os.chdir(test_project_path.as_posix())
    mypythontools.paths.PROJECT_PATHS.reset_paths()

    yield

    os.chdir(cwd_backup.as_posix())
