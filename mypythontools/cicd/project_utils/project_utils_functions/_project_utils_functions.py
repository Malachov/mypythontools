"""Module with functions for project_utils_functions subpackage."""

from __future__ import annotations
from typing import Sequence
import ast
import subprocess

import mylogging

from ....helpers.misc._misc import check_script_is_available, get_console_str_with_quotes, delete_files
from ....helpers.paths import PROJECT_PATHS, validate_path, PathLike
from ....helpers.type_hints import validate_sequence

# Lazy loaded
# from git import Repo


def reformat_with_black(
    root_path: None | PathLike = None,
    extra_args: Sequence[str] = ("--quiet",),
) -> None:
    """Reformat code with black.

    Args:
        root_path (None | PathLike, optional): Root path of project. If None, will be inferred.
            Defaults to None.
        extra_args (Sequence[str], optional): Some extra args for black. Defaults to ("--quiet,").

    Example:
        >>> reformat_with_black()
    """
    check_script_is_available("black", "black")
    validate_sequence(extra_args, "extra_args")

    root_path = validate_path(root_path) if root_path else PROJECT_PATHS.root

    command = f"black . {' '.join(extra_args)}"

    try:
        result = subprocess.run(command, check=True, cwd=root_path, shell=True)
        if result.returncode != 0:
            raise RuntimeError
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
    """Stage all changes, commit, add tag and push.

    If tag = '__version__', than tag is inferred from __init__.py.

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
        result = subprocess.run(git_command, check=True, cwd=PROJECT_PATHS.root.as_posix(), shell=True)
        if result.returncode != 0:
            raise RuntimeError
    except (Exception,):
        git.repo.Repo(PROJECT_PATHS.root.as_posix()).delete_tag(tag)  # type: ignore
        mylogging.traceback(
            "Push to git failed. Version restored and created git tag deleted."
            f"Try to run command \n\n{git_command}\n\n manually in your root {PROJECT_PATHS.root}."
        )
        raise


def set_version(
    version: str = "increment",
    init_path: None | PathLike = None,
) -> None:
    """Change your version in your __init__.py file.

    Args:
        version (str, optional): Form that is used in __init__, so for example "1.2.3". Do not use 'v'
            appendix. If version is 'increment', it will increment your __version__ in you __init__.py by
            0.0.1. Defaults to "increment".
        init_path (None | PathLike, optional): Path of file where __version__ is defined.
            Usually __init__.py. If None, will be inferred. Defaults to None.

    Raises:
        ValueError: If no __version__ is find.
    """
    init_path = validate_path(init_path) if init_path else PROJECT_PATHS.init

    is_valid = version == "increment" or (
        len(version.split(".")) == 3 and all([i.isdecimal() for i in version.split(".")])
    )

    if not is_valid:
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


def get_version(init_path: None | PathLike = None) -> str:
    """Get version info from __init__.py file.

    Args:
        init_path (None | PathLike, optional): Path to __init__.py file. If None, will be inferred.
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


def sphinx_docs_regenerate(
    docs_path: None | PathLike = None,
    build_locally: bool = False,
    git_add: bool = True,
    keep: Sequence[PathLike] = (
        "conf.py",
        "index.rst",
        "_static",
        "_templates",
        "content/**",
    ),
    delete: Sequence[PathLike] = ("modules.rst",),
) -> None:
    """Generate all rst files necessary for sphinx documentation generation with sphinx-apidoc.

    It automatically delete removed and renamed files.

    Note:
        All the files except in 'keep' parametert ['conf.py', 'index.rst', '_static', '_templates', 'content']
        will be deleted!!! Because if some files would be deleted or renamed, rst would stay and html was
        generated. If you have some extra files or folders in docs source - add it to content folder or to
        `keep` parameter.

    Function suppose sphinx build and source in separate folders...

    Args:
        docs_path (None | PathLike, optional): Where source folder is. If None, will be inferred.
            Defaults to None.
        build_locally (bool, optional): If true, build folder with html files locally.
            Defaults to False.
        git_add (bool, optional): Whether to add generated files to stage. False mostly for
            testing reasons. Defaults to True.
        keep (Sequence[PathLike], optional): List of files and folder names that will not be
            deleted. Deletion is because if some file would be renamed or deleted, rst docs would still stay.
            Glob-style patterns can be used.
            Defaults to ("conf.py", "index.rst", "_static", "_templates", "content/**").
        delete (Sequence[PathLike], optional): If delete some files from generated rst files. For example to
            have no errors in sphinx build for unused modules, or for internal modules. Glob-style patterns
            can be used. Defaults to ("**/**_internal**")

    Note:
        Function suppose structure of docs like::

            -- docs
            -- -- source
            -- -- -- conf.py
            -- -- make.bat
    """
    check_script_is_available("sphinx-apidoc", "sphinx")

    validate_sequence(keep, keep)
    validate_sequence(delete, delete)

    docs_path = validate_path(docs_path) if docs_path else PROJECT_PATHS.docs

    docs_source_path = docs_path / "source"

    for file in docs_source_path.iterdir():
        if not any((file.match(str(pattern)) for pattern in keep)):
            delete_files(file)

    source_path = get_console_str_with_quotes(PROJECT_PATHS.app)

    # if ve
    # apidoc_path = sphinx-apidoc

    apidoc_command = f"sphinx-apidoc --module-first --force --separate -o source {source_path}"

    result = subprocess.run(
        apidoc_command,
        cwd=docs_path,
        check=True,
    )
    if result.returncode != 0:
        raise RuntimeError

    if delete:
        for file in docs_source_path.iterdir():
            if any((file.match(str(pattern)) for pattern in delete)):
                delete_files(file)

    if build_locally:
        result = subprocess.run("make html", cwd=docs_path, check=True)
        if result.returncode != 0:
            raise RuntimeError

    if git_add:
        result = subprocess.run(
            "git add docs",
            cwd=PROJECT_PATHS.root.as_posix(),
            check=True,
        )
        if result.returncode != 0:
            raise RuntimeError


def generate_readme_from_init(git_add: bool = True) -> None:
    """Generate README file from __init__.py docstrings.

    Because i had very similar things in main __init__.py and in readme. It was to maintain news
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
        result = subprocess.run(
            f"git add {PROJECT_PATHS.readme}",
            cwd=PROJECT_PATHS.root.as_posix(),
            check=True,
        )
        if result.returncode != 0:
            raise RuntimeError
