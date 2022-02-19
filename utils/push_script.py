"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""

# import os
# import inspect
from pathlib import Path
import sys

# Find paths and add to sys.path to be able to use local version and not installed mypythontools version
root_path_str = Path(__file__).parents[1].as_posix()
# root = Path(os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)).parents[1]

if root_path_str not in sys.path:
    sys.path.insert(0, root_path_str)

from mypythontools import cicd

if __name__ == "__main__":
    # All the parameters can be overwritten via CLI args
    cicd.project_utils.project_utils_pipeline(
        reformat=True,
        test=True,
        test_options={"virtualenvs": ["venv/37", "venv/310"]},
        version="increment",
        sphinx_docs=True,
        sync_requirements=False,
        commit_and_push_git=True,
        commit_message="New commit",
        tag="__version__",
        tag_mesage="New version",
        deploy=False,
        allowed_branches=("master", "main"),
    )
