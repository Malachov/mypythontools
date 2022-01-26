"""Runs before every pytest test. Used automatically (at least at VS Code)."""

import os
import inspect
from pathlib import Path
import sys
import pytest


# TODO delete me
import sys
from pathlib import Path

sys.path.insert(0, (Path.cwd().parent / "mylogging").as_posix())
import mylogging


# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
root = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parent

if root not in sys.path:
    sys.path.insert(0, root.as_posix())

from mypythontools import cicd
from mypythontools import helpers

cicd.tests.setup_tests(matplotlib_test_backend=True)

# Can be loaded from tests here or tests in test project
test_project_path = (
    Path("tests").resolve() / "tested_project" if Path.cwd().name != "tested_project" else Path.cwd()
)


@pytest.fixture(autouse=True)
def setup_tests():
    """Configure tests. Runs automatically from pytest and is called if running from file."""
    cwd_backup = Path.cwd()

    os.chdir(test_project_path.as_posix())
    helpers.paths.PROJECT_PATHS.reset_paths()

    yield

    os.chdir(cwd_backup.as_posix())
