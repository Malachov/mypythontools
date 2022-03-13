"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""



# TODO delete me
import sys
from pathlib import Path
sys.path.insert(0, (Path.cwd().parent / 'mypythontools_cicd').as_posix())
import mypythontools_cicd

from mypythontools_cicd.project_utils import project_utils_pipeline

if __name__ == "__main__":
    # All the parameters can be overwritten via CLI args
    project_utils_pipeline(
        reformat=True,
        test=True,
        test_options={"virtualenvs": ["venv/37", "venv/310"]},
        version="increment",
        docs=True,
        sync_requirements=False,
        commit_and_push_git=True,
        commit_message="New commit",
        tag="__version__",
        tag_message="New version",
        deploy=True,
        allowed_branches=("master", "main"),
    )

    # project_utils_pipeline(
    #     do_only="deploy",
    # )
