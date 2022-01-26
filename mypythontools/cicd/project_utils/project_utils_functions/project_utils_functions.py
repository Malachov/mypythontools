"""Module with functions for project_utils_functions subpackage."""

from __future__ import annotations
import ast
import importlib.util
from pathlib import Path
import subprocess

import mylogging

from ....helpers.misc.misc import get_console_str_with_quotes
from ....helpers.paths import PROJECT_PATHS, validate_path

# Lazy loaded
# from git import Repo


def reformat_with_black(  # pylint: disable="dangerous-default-value"
    root_path: None | str | Path = None,
    extra_args: list[str] = ["--quiet"],
) -> None:
    """Reformat code with black.

    Args:
        root_path (None | str | Path, optional): Root path of project. If None, will be inferred.
            Defaults to None.
        extra_args (list[str], optional): Some extra args for black. Defaults to ["--quiet"].

    Example:
        >>> reformat_with_black()
    """
    root_path = validate_path(root_path) if root_path else PROJECT_PATHS.root

    try:
        subprocess.run(f"black . {' '.join(extra_args)}", check=True, cwd=root_path)
    except FileNotFoundError:
        mylogging.traceback(
            "FileNotFoundError can happen if `black` is not installed. Check it with pip list in used "
            "python interpreter."
        )
        raise
    except (Exception,):
        mylogging.traceback(
            "Reformatting with `black` failed. Check if it's installed, check logged error, "
            "then try format manually with \n\nblack .\n\n"
        )
        raise


def git_push(
    commit_message: str,
    tag: str = "__version__",
    tag_message: str = "New version",
) -> None:
    """Stage all changes, commit, add tag and push. If tag = '__version__', than tag
    is inferred from __init__.py.

    Args:
        commit_message (str): Commit message.
        tag (str, optional): Define tag used in push. If tag is '__version__', than is automatically generated
            from __init__ version. E.g from '1.0.2' to 'v1.0.2'.  Defaults to '__version__'.
        tag_message (str, optional): Message in annotated tag. Defaults to 'New version'.
    """

    import git.repo

    git_command = f"git add . && git commit -m {get_console_str_with_quotes(commit_message)} && git push"

    if tag == "__version__":
        tag = f"v{get_version()}"

    if tag:
        if not tag_message:
            tag_message = "New version"

        git.repo.Repo(PROJECT_PATHS.root.as_posix()).create_tag(tag, message=tag_message)
        git_command += " --follow-tags"

    try:
        subprocess.run(git_command, check=True, cwd=PROJECT_PATHS.root.as_posix(), shell=True)
    except (Exception,):
        git.repo.Repo(PROJECT_PATHS.root.as_posix()).delete_tag(tag)  # type: ignore
        mylogging.traceback(
            "Push to git failed. Version restored and created git tag deleted."
            f"Try to run command \n\n{git_command}\n\n manually in your root {PROJECT_PATHS.root}."
        )
        raise


def set_version(
    version: str = "increment",
    init_path: None | str | Path = None,
) -> None:
    """Change your version in your __init__.py file.


    Args:
        version (str, optional): Form that is used in __init__, so for example "1.2.3". Do not use 'v'
            appendix. If version is 'increment', it will increment your __version__ in you __init__.py by
            0.0.1. Defaults to "increment".
        init_path (None | str | Path, optional): Path of file where __version__ is defined.
            Usually __init__.py. If None, will be inferred. Defaults to None.

    Raises:
        ValueError: If no __version__ is find.
    """

    init_path = validate_path(init_path) if init_path else PROJECT_PATHS.init

    if version == "increment" or (
        len(version.split(".")) == 3 and all([i.isdecimal() for i in version.split(".")])
    ):
        pass

    else:
        raise ValueError(
            mylogging.format_str(
                "Version not validated. Version has to be of form '1.2.3'. Three digits and two dots. "
                f"You used {version}"
            )
        )

    with open(init_path.as_posix(), "r") as init_file:

        list_of_lines = init_file.readlines()

        found = False

        for i, j in enumerate(list_of_lines):
            if j.startswith("__version__"):

                found = True

                delimiter = '"' if '"' in j else "'"
                delimited = j.split(delimiter)

                if version == "increment":
                    version_list = delimited[1].split(".")
                    version_list[2] = str(int(version_list[2]) + 1)
                    delimited[1] = ".".join(version_list)

                else:
                    delimited[1] = version

                list_of_lines[i] = delimiter.join(delimited)
                break

        if not found:
            raise ValueError(
                mylogging.format_str("__version__ variable not found in __init__.py. Try set init.")
            )

    with open(init_path.as_posix(), "w") as init_file:

        init_file.writelines(list_of_lines)


def get_version(init_path: None | str | Path = None) -> str:
    """Get version info from __init__.py file.

    Args:
        init_path (None | str | Path, optional): Path to __init__.py file. If None, will be inferred.
            Defaults to None.

    Returns:
        str: String of version from __init__.py.

    Raises:
        ValueError: If no __version__ is find. Try set init_path...

    Example:
        >>> version = get_version()
        >>> len(version.split(".")) == 3 and all([i.isdecimal() for i in version.split(".")])
        True
    """

    init_path = validate_path(init_path) if init_path else PROJECT_PATHS.init

    with open(init_path.as_posix(), "r") as init_file:

        for line in init_file:

            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]

        raise ValueError(mylogging.format_str("__version__ variable not found in __init__.py."))


def sphinx_docs_regenerate(  # pylint: disable="dangerous-default-value"
    docs_path: None | str | Path = None,
    build_locally: bool = False,
    git_add: bool = True,
    exclude_paths: list[str | Path] = [],
    delete: list[str | Path] = ["modules.rst"],
) -> None:
    """This will generate all rst files necessary for sphinx documentation generation with sphinx-apidoc.
    It automatically delete removed and renamed files.

    Note:
        All the files except ['conf.py', 'index.rst', '_static', '_templates'] will be deleted!!!
        Because if some files would be deleted or renamed, rst would stay and html was generated.
        If you have some extra files or folders in docs source - add it to `exclude_paths` list.

    Function suppose sphinx build and source in separate folders...

    Args:
        docs_path (None | str | Path, optional): Where source folder is. If None, will be inferred.
            Defaults to None.
        build_locally (bool, optional): If true, build folder with html files locally.
            Defaults to False.
        git_add (bool, optional): Whether to add generated files to stage. False mostly for
            testing reasons. Defaults to True.
        exclude_paths (list[str | Path], optional): List of files and folder names that will not be deleted.
            ['conf.py', 'index.rst', '_static', '_templates'] are excluded by default. Defaults to [].
        delete (list[str | Path], optional): If delete some files (for example to have no errors in sphinx
            build for unused modules)

    Note:
        Function suppose structure of docs like::

            -- docs
            -- -- source
            -- -- -- conf.py
            -- -- make.bat
    """

    if not importlib.util.find_spec("sphinx"):
        raise ImportError(
            mylogging.format_str(
                "Sphinx library is necessary for docs generation. Install via \n\npip install sphinx\n\n"
            )
        )

    docs_path = validate_path(docs_path) if docs_path else PROJECT_PATHS.docs

    docs_source_path = docs_path.resolve() / "source"

    for file in docs_source_path.iterdir():
        if file.name not in [
            "conf.py",
            "index.rst",
            "_static",
            "_templates",
            *exclude_paths,
        ]:
            try:
                file.unlink()
            except (OSError, PermissionError):
                pass

    apidoc_command = f"sphinx-apidoc -f -e -o source {get_console_str_with_quotes(PROJECT_PATHS.app)}"
    subprocess.run(
        apidoc_command,
        cwd=docs_path,
        check=True,
    )

    if delete:
        for i in delete:
            (docs_source_path / i).unlink()

    if build_locally:
        subprocess.run(["make", "html"], cwd=docs_path, check=True)

    if git_add:
        subprocess.run(
            ["git", "add", "docs"],
            cwd=PROJECT_PATHS.root.as_posix(),
            check=True,
        )


def generate_readme_from_init(git_add: bool = True) -> None:
    """Because i had very similar things in main __init__.py and in readme. It was to maintain news
    in code. For better simplicity i prefer write docs once and then generate. One code, two use cases.

    Why __init__? - Because in IDE on mouseover developers can see help.
    Why README.md? - Good for github.com

    Args:
        git_add (bool, optional): Whether to add generated files to stage. False mostly
            for testing reasons. Defaults to True.
    """

    with open(PROJECT_PATHS.init.as_posix()) as init_file:
        file_contents = init_file.read()
    module = ast.parse(file_contents)
    docstrings = ast.get_docstring(module)

    if docstrings is None:
        docstrings = ""

    with open(PROJECT_PATHS.readme.as_posix(), "w") as file:
        file.write(docstrings)

    if git_add:
        subprocess.run(
            [
                "git",
                "add",
                PROJECT_PATHS.readme,
            ],
            cwd=PROJECT_PATHS.root.as_posix(),
            check=True,
        )
