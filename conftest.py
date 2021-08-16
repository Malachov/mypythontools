import os
import inspect
from pathlib import Path
import sys

# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
ROOT_PATH = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parent
TEST_PATH = ROOT_PATH / "tests"

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH.as_posix())

import mypythontools

mypythontools.tests.setup_tests()
