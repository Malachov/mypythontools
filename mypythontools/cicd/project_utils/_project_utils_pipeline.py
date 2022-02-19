"""Module with functions for 'project_utils' subpackage."""

from __future__ import annotations
from typing import Sequence, Any
import os
import sys

import mylogging

from .. import tests
from .. import venvs
from ...helpers.config import ConfigBase, MyProperty
from ...helpers.misc._misc import GLOBAL_VARS
from ...helpers.paths import PROJECT_PATHS, PathLike
from ...helpers.type_hints import validate_sequence
from ..deploy import deploy_to_pypi
from .project_utils_functions import (
    get_version,
    git_push,
    reformat_with_black,
    set_version,
    sphinx_docs_regenerate,
)

# Lazy loaded
# from git import Repo


class PipelineConfig(ConfigBase):
    """Allow to setup CICD pipeline."""

    @MyProperty
    @staticmethod
    def reformat() -> bool:
        """Reformat all python files with black. Setup parameters in pyproject.toml.

        Type:
            bool

        Default:
            True.
        """
        return True

    @MyProperty
    @staticmethod
    def test() -> bool:
        """Run pytest tests.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    @staticmethod
    def test_options() -> None | dict:
        """Check tests module and function run_tests for what parameters you can use.

        Type:
            None | dict

        Default:
            None

        Example:
            ``{"virtualenvs": ["venv/37", "venv/310], "test_coverage": True, "verbose": False}``
        """
        return None

    @MyProperty
    @staticmethod
    def version() -> str:
        """Overwrite __version__ in __init__.py.

        Type:
            str

        Default:
            'increment'.

        Version has to be in format like '1.0.3' three digits and two dots. If 'None', nothing will happen. If
        'increment', than it will be updated by 0.0.1..
        """
        return "increment"

    @MyProperty
    @staticmethod
    def sphinx_docs() -> bool:
        """Whether generate sphinx apidoc and generate rst files for documentation. Some files in docs source
        can be deleted - check `sphinx_docs` docstrings for details.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    @staticmethod
    def sync_requirements() -> bool | PathLike:
        """Check requirements.txt and update all the libraries.

        Type:
            bool | PathLike

        Default:
            False

        You can use path to requirements. If True, then path is inferred.
        """
        return False

    @MyProperty
    @staticmethod
    def commit_and_push_git() -> bool:
        """Whether push to github or not.

        Type:
            bool

        Default:
            True
        """
        return True

    @MyProperty
    @staticmethod
    def commit_message() -> str:
        """Commit message.

        Type:
            str

        Default:
            'New commit'
        """
        return "New commit"

    @MyProperty
    @staticmethod
    def tag() -> str:
        """Tag. E.g 'v1.1.2'. If '__version__', get the version.

        Type:
            str

        Default:
            '__version__'
        """
        return "__version__"

    @MyProperty
    @staticmethod
    def tag_mesage() -> str:
        """Tag message.

        Type:
            bool

        Default:
            'New version'
        """
        return "New version"

    @MyProperty
    @staticmethod
    def deploy() -> bool:
        """Deploy to PYPI.

        `TWINE_USERNAME` and `TWINE_PASSWORD` are used for authorization.

        Type:
            bool

        Default:
            False
        """
        return False

    @MyProperty
    @staticmethod
    def allowed_branches() -> None | Sequence[str]:
        """Pipeline runs only on defined branches.

        Type:
            None | Sequence[str]

        Default:
            ["master", "main"]
        """
        return ["master", "main"]


def project_utils_pipeline(
    config: PipelineConfig = None,
    reformat: bool = True,
    test: bool = True,
    test_options: None | dict[str, Sequence[PathLike]] | dict[str, Any] = None,
    version: str = "increment",
    sphinx_docs: bool = True,
    sync_requirements: bool | PathLike = False,
    commit_and_push_git: bool = True,
    commit_message: str = "New commit",
    tag: str = "__version__",
    tag_mesage: str = "New version",
    deploy: bool = False,
    allowed_branches: None | Sequence[str] = ("master", "main"),
) -> None:
    """Run pipeline for pushing and deploying app.

    Can run tests, generate rst files for sphinx docs, push to github and deploy to pypi. All params can be
    configured not only with function params, but also from command line with params and therefore callable
    from terminal and optimal to run from IDE (for example with creating simple VS Code task).

    Some function suppose some project structure (where are the docs, where is __init__.py etc.).
    If you are issuing some error, try functions directly, find necessary paths in parameters
    and set paths that are necessary in paths module.

    Note:
        Beware that pushing to git create a commit and add all the changes.

    Check utils module docs for implementation example. Some functions have specific parameters and here can
    be used just True / False. Use function separately if needed.

    Args:
        config (PipelineConfig, optional): It is possible to configure all the params with CLI args from
            terminal. Just create script, where create config, use 'config.with_argparse()' and call
            project_utils_pipeline(config=config). Example usage 'python your_script.py --deploy True'
        reformat (bool, optional): Reformat all python files with black. Setup parameters in
            `pyproject.toml`, especially setup `line-length`. Defaults to True.
        test (bool, optional): Whether run pytest tests. Defaults to True.
        test_options (None | dict, optional): Parameters of tests function e.g.
            ``{"virtualenvs": ["venv/37", "venv/310], "test_coverage": True, "verbose": False}``.
            Defaults to None.
        version (str, optional): New version. E.g. '1.2.5'. If 'increment', than it's auto
            incremented. E.g from '1.0.2' to 'v1.0.3'. If empty string "" or not value arg in CLI,
            then version is not changed. 'Defaults to "increment".
        sphinx_docs(bool, optional): Whether generate sphinx apidoc and generate rst files for documentation.
            Some files in docs source can be deleted - check `sphinx_docs` docstrings for details.
            Defaults to True.
        sync_requirements(bool | PathLike, optional): Check requirements.txt and update all the libraries.
            You can use path to requirements. If True, then path is inferred. Defaults to False.
        commit_and_push_git (bool, optional): Whether push repository on git with commit_message, tag and tag
            message. Defaults to True.
        commit_message (str, optional): Git message. Defaults to 'New commit'.
        tag (str, optional): Used tag. If tag is '__version__', than updated version from __init__
            is used.  If empty string "" or not value arg in CLI, then tag is not created.
            Defaults to __version__.
        tag_mesage (str, optional): Tag message. Defaults to New version.
        deploy (bool, optional): Whether deploy to PYPI. `TWINE_USERNAME` and `TWINE_PASSWORD`
            are used for authorization. Defaults to False.
        allowed_branches (None | Sequence[str], optional): As there are stages like pushing to git or to PyPi,
            it's better to secure it to not to be triggered on some feature branch. If not one of
            defined branches, error is raised. Defaults to ("master", "main").

    Example:
        Recommended use is from IDE (for example with Tasks in VS Code). Check utils docs for how
        to use it. You can also use it from python...

        Put it in `if __name__ == "__main__":` block::

            project_utils_pipeline(commit_and_push_git=False, deploy=False, allowed_branches=None)

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
                "sync_requirements": sync_requirements,
                "sphinx_docs": sphinx_docs,
                "commit_and_push_git": commit_and_push_git,
                "commit_message": commit_message,
                "tag": tag,
                "tag_mesage": tag_mesage,
                "deploy": deploy,
                "allowed_branches": allowed_branches,
            }
        )

    if not GLOBAL_VARS.is_tested:
        config.with_argparse()

    if config.allowed_branches:
        import git.repo

        validate_sequence(allowed_branches, "allowed_branches")

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
    if config.sync_requirements:
        sync_requirements = "infer" if config.sync_requirements is True else config.sync_requirements
        if not venvs.is_venv:
            raise RuntimeError(
                mylogging.format_str("'sync_requirements' available only if using virtualenv.")
            )
        my_venv = venvs.Venv(sys.prefix)
        my_venv.create()
        my_venv.sync_requirements(sync_requirements)

    if config.test:
        if not config.test_options:
            config.test_options = {}

        tests.run_tests(**config.test_options)

    if config.reformat:
        reformat_with_black()

    if config.version and config.version != "None":
        original_version = get_version()
        set_version(config.version)

    try:
        if config.sphinx_docs:
            sphinx_docs_regenerate()

        if config.commit_and_push_git:
            git_push(
                commit_message=config.commit_message,
                tag=config.tag,
                tag_message=config.tag_mesage,
            )
    except Exception:  # pylint: disable=broad-except
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
    except Exception:  # pylint: disable=broad-except
        mylogging.traceback(
            "Deploy failed, but pushed to repository already. Deploy manually. Version already changed.",
            level="CRITICAL",
        )
