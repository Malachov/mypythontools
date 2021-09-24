import os
import inspect
from pathlib import Path
import sys

# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
ROOT_PATH = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parents[1]

if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH.as_posix())

import mypythontools

if __name__ == "__main__":
    mypythontools.utils.push_pipeline(
        sphinx_docs=["pyvueeel-tutorial.rst"],
        test=False,
        deploy=True,
    )
