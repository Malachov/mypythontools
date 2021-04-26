import SET_YOUR_NAME

if __name__ == "__main__":

    SET_YOUR_NAME.utils.push_pipeline(
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
