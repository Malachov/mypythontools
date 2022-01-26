"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""

import os
import inspect
from pathlib import Path
import sys

# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
root = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parents[1]

if root not in sys.path:
    sys.path.insert(0, root.as_posix())

from mypythontools import cicd

if __name__ == "__main__":
    # All the parameters can be overwritten via CLI args
    cicd.project_utils.project_utils_pipeline(
        sphinx_docs=["pyvueeel-tutorial.rst"],
        test=False,
        # deploy=True,
    )
