import mypythontools


if __name__ == "__main__":
    # All the parameters can be overwritten via CLI args
    mypythontools.project_utils_functions.project_utils_pipeline(
        tests=True,
        version="increment",  # increment by 0.0.1
        sphinx_docs=True,
        git_params={
            # If using VS Code task, set git_params there!
            "commit_message": "New commit",
            "tag": "__version__",  # __version__ take version from __init__.
            "tag_mesage": "New version",
        },
        deploy=False,
    )
