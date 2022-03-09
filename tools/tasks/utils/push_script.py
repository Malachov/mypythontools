from mypythontools import cicd


if __name__ == "__main__":
    # All the parameters can be overwritten via CLI args
    cicd.project_utils.project_utils_pipeline(
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
        deploy=False,
        allowed_branches=("master", "main"),
    )
