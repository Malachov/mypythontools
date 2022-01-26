"""Module with functions for 'project_utils' subpackage."""

from __future__ import annotations
import argparse
import sys
import os

import mylogging

from ...helpers.misc.misc import str_to_bool, GLOBAL_VARS
from .. import tests
from ..deploy import deploy_to_pypi
from ...helpers.paths import PROJECT_PATHS
from ...helpers.config import ConfigBase, MyProperty
from .project_utils_functions import (
    get_version,
    git_push,
    reformat_with_black,
    set_version,
    sphinx_docs_regenerate,
)

# Lazy loaded
# from git import Repo
# import json


class PipelineConfig(ConfigBase):
    @MyProperty
    def reformat() -> bool:
        """Whether reformat all python files with black. Setup parameters in pyproject.toml.
        Defaults to True."""
        return True

    @MyProperty
    def test() -> bool:
        """Whether run pytest. Defaults to: True."""
        return True

    @MyProperty
    def test_options() -> dict:
        """Check tests module and function run_tests for what parameters you can use. Defaults to: {}."""
        return {}

    @MyProperty
    def version() -> str:
        """Version in __init__.py will be overwritten. Version has to be in format like '1.0.3'
        three digits and two dots. If 'None', nothing will happen. If 'increment', than it will be
        updated by 0.0.1.. Defaults to: 'increment'."""
        return "increment"

    @MyProperty
    def sphinx_docs() -> bool | list[str]:
        """Whether run apidoc to create files for example for readthedocs. Defaults to: True."""
        return True

    @MyProperty
    def commit_and_push_git() -> bool:
        """Whether push to github or not. Defaults to: True."""
        return True

    @MyProperty
    def commit_message() -> str:
        """Commit message. Defaults to: 'New commit'."""
        return "New commit"

    @MyProperty
    def tag() -> str:
        """Tag. E.g 'v1.1.2'. If '__version__', get the version. Defaults to: '__version__'."""
        return "__version__"

    @MyProperty
    def tag_mesage() -> str:
        """Tag message. Defaults to: 'New version'."""
        return "New version"

    @MyProperty
    def deploy() -> bool:
        """Whether deploy to PYPI. `TWINE_USERNAME` and `TWINE_PASSWORD` are used for authorization.
        Defaults to False."""
        return False

    @MyProperty
    def allowed_branches() -> list[str]:
        """Pipeline runs only on defined branches."""
        return ["master", "main"]


def project_utils_pipeline(  # pylint: disable="dangerous-default-value"
    config: PipelineConfig = None,
    reformat: bool = True,
    test: bool = True,
    test_options: dict = {},
    version: str = "increment",
    sphinx_docs: bool | list[str] = True,
    commit_and_push_git: bool = True,
    commit_message: str = "New commit",
    tag: str = "__version__",
    tag_mesage: str = "New version",
    deploy: bool = False,
    allowed_branches: list[str] = ["master", "main"],
) -> None:  # pylint: disable=dangerous-default-value
    """Run pipeline for pushing and deploying app. Can run tests, generate rst files for sphinx docs,
    push to github and deploy to pypi. All params can be configured not only with function params,
    but also from command line with params and therefore callable from terminal and optimal to run
    from IDE (for example with creating simple VS Code task).

    Some function suppose some project structure (where are the docs, where is __init__.py etc.).
    If you are issuing some error, try functions directly, find necessary paths in parameters
    and set paths that are necessary in paths module.

    Note:
        Beware that pushing to git create a commit and add all the changes.

    Check utils module docs for implementation example.

    Args:
        config (PipelineConfig, optional): It is possible to configure all the params with CLI args from
            terminal. Just create script, where create config, use 'config.with_argparse()' and call
            project_utils_pipeline(config=config). Example usage 'python your_script.py --deploy True'
        reformat (bool, optional): Reformat all python files with black. Setup parameters in
            `pyproject.toml`, especially setup `line-length`. Defaults to True.
        test (bool, optional): Whether run pytest tests. Defaults to True.
        test_options (dict, optional): Parameters of tests function e.g.
            `{"test_coverage": True, "verbose": False, "use_virutalenv":True}`. Defaults to {}.
        version (str, optional): New version. E.g. '1.2.5'. If 'increment', than it's auto
            incremented. E.g from '1.0.2' to 'v1.0.3'. If empty string "" or not value arg in CLI,
            then version is not changed. 'Defaults to "increment".
        sphinx_docs(bool | list[str], optional): Whether generate sphinx apidoc and generate rst
            files for documentation. Some files in docs source can be deleted - check `sphinx_docs`
            docstrings for details and insert `exclude_paths` list if have some extra files other
            than ['conf.py', 'index.rst', '_static', '_templates']. Defaults to True.
        commit_and_push_git (bool, optional): Whether push repository on git with git_message, tag and tag
            message. Defaults to True.
        git_message (str, optional): Git message. Defaults to 'New commit'.
        tag (str, optional): Used tag. If tag is '__version__', than updated version from __init__
            is used.  If empty string "" or not value arg in CLI, then tag is not created.
            Defaults to __version__.
        tag_mesage (str, optional): Tag message. Defaults to New version.
        deploy (bool, optional): Whether deploy to PYPI. `TWINE_USERNAME` and `TWINE_PASSWORD`
            are used for authorization. Defaults to False.
        allowed_branches (list[str], optional): As there are stages like pushing to git or to PyPi,
            it's better to secure it to not to be triggered on some feature branch. If not one of
            defined branches, error is raised. Defaults to ["master", "main"].

    Example:
        Recommended use is from IDE (for example with Tasks in VS Code). Check utils docs for how
        to use it. You can also use it from python...

        Put it in `if __name__ == "__main__":` block

        >>> project_utils_pipeline(commit_and_push_git=False, deploy=False)

        It's also possible to use CLI and configure it via args. This example just push repo to PyPi.

            python path-to-project/utils/push_script.py --deploy True --test False --reformat False --version --push_git False --sphinx_docs False
    """
    if not config:
        config = PipelineConfig()
        config.update(
            {
                "reformat": reformat,
                "test": test,
                "test_options": test_options,
                "version": version,
                "sphinx_docs": sphinx_docs,
                "commit_and_push_git": commit_and_push_git,
                "commit_message": commit_message,
                "tag": tag,
                "tag_mesage": tag_mesage,
                "deploy": deploy,
                "allowed_branches": allowed_branches,
            }
        )

    if config.allowed_branches and not GLOBAL_VARS.IS_TESTED:
        import git.repo

        branch = git.repo.Repo(PROJECT_PATHS.root.as_posix()).active_branch.name

        if branch not in config.allowed_branches:
            raise RuntimeError(
                mylogging.critical(
                    (
                        "Pipeline started on branch that is not allowed."
                        "If you want to use it anyway, add it to allowed_branches parameter and "
                        "turn off changing version and creating tag."
                    ),
                    caption="Pipeline error",
                )
            )

    # Do some checks before run pipeline so not need to rollback eventually
    if config.deploy:
        usr = os.environ.get("TWINE_USERNAME")
        pas = os.environ.get("TWINE_PASSWORD")

        if not usr or not pas:
            raise KeyError(
                mylogging.format_str("Setup env vars TWINE_USERNAME and TWINE_PASSWORD to use deploy.")
            )

    if config.reformat:
        reformat_with_black()

    if config.test:
        if isinstance(config.test_options, str):
            import json

            config.test_options = json.loads(config.test_options)

        tests.run_tests(**config.test_options)

    if config.version and config.version != "None":
        original_version = get_version()
        set_version(config.version)

    try:
        if isinstance(config.sphinx_docs, list):
            sphinx_docs_regenerate(exclude_paths=config.sphinx_docs)
        elif config.sphinx_docs:
            sphinx_docs_regenerate()

        if config.commit_and_push_git:
            git_push(
                commit_message=config.commit_message,
                tag=config.tag,
                tag_message=config.tag_mesage,
            )
    except Exception:
        if config.version:
            set_version(original_version)  # type: ignore

        mylogging.traceback(
            "Utils pipeline failed. Original version restored. Nothing was pushed to repo, "
            "you can restart pipeline."
        )
        return

    try:
        if config.deploy:
            deploy_to_pypi()
    except Exception:
        mylogging.traceback(
            "Deploy failed, but pushed to repository already. Deploy manually. Version already changed.",
            level="CRITICAL",
        )
