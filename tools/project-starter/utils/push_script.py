from mypythontools import cicd


if __name__ == "__main__":
    # All the parameters usually overwritten via CLI args
    cicd.project_utils.project_utils_pipeline(
        # test=True,
        # version="increment",  # increment by 0.0.1
        # sphinx_docs=True,
        # commit_and_push_git = True,
        # commit_message = "New commit",
        # tag="__version__",
        # deploy=False,
    )
