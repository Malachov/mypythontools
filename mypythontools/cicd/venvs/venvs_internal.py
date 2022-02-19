"""Module with functions for 'venvs' subpackage."""

from __future__ import annotations
from typing import Sequence
import platform
import subprocess
import shutil
from pathlib import Path
from ast import literal_eval
import sys

from typing_extensions import Literal

import mylogging

from ...helpers.paths import PROJECT_PATHS, validate_path, PathLike
from ...helpers.misc import get_console_str_with_quotes


class Venv:
    """You can create new venv or sync it's dependencies.

    Example:
        >>> from pathlib import Path
        ...
        >>> path = "venv/310"
        >>> venv = Venv(path)
        >>> venv.create()  # If already exists, it's skipped
        >>> venv.install_library("colorama==0.3.9")
        >>> "colorama==0.3.9" in venv.list_packages()
        True
        >>> venv.sync_requirements()  # There ia a 8.0.3 in requirements.txt
        >>> "colorama==0.4.4" in venv.list_packages()
        True
        >>> venv.remove()
        >>> Path(path).exists()
        False
    """

    def __init__(self, venv_path: PathLike) -> None:
        """Init the venv class. To create or update it, you can call extra functions.

        Args:
            venv_path(PathLike): Path of venv. E.g. `venv`

        Raises:
            FileNotFoundError: No folder found on defined path.
        """
        self.venv_path = Path(venv_path).resolve()
        """Path to venv prefix, e.g. .../venv"""

        if not self.venv_path.exists():
            self.venv_path.mkdir()

        self.venv_path_console_str = get_console_str_with_quotes(self.venv_path)

        if not self.venv_path.exists():
            self.venv_path.mkdir(parents=True, exist_ok=True)

        if platform.system() == "Windows":
            activate_path = self.venv_path / "Scripts" / "activate.bat"
            self.executable = self.venv_path / "Scripts" / "python.exe"
            self.create_command = f"python -m virtualenv {self.venv_path_console_str}"
            self.activate_command = get_console_str_with_quotes(activate_path.as_posix())
            scripts_path = self.venv_path / "Scripts"
        else:
            self.executable = self.venv_path / "bin" / "python"
            self.create_command = f"python3 -m virtualenv {self.venv_path_console_str}"
            self.activate_command = (
                f"source {get_console_str_with_quotes(self.venv_path / 'bin' / 'activate')}"
            )
            scripts_path = self.venv_path / "bin"

        self.installed = True if (self.executable).exists() else False

        # TODO verify on linux
        self.scripts_path: Path = scripts_path
        """Path to the executables. Can be directly used in terminal. Some libraries cannot use
        ``python -m package`` syntax and therefore it can be called from scripts folder."""

        self.subprocess_prefix = (
            f"{self.activate_command} && {get_console_str_with_quotes(self.executable.as_posix())} -m "
        )
        """Run as module, so library can be directly call afterwards.
        Can be directly used in terminal.
        E.g. ``.../Scripts/activate.bat && .../venv/Scripts/python.exe -m``"""

    def create(self) -> None:
        """Create virtual environment. If it already exists, it will be skipped and nothing happens."""
        if not self.installed:
            try:
                result = subprocess.run(self.create_command, check=True, capture_output=True, shell=True)
                if result.returncode != 0:
                    raise RuntimeError
            except Exception:
                mylogging.traceback("Creation of venv failed. Check logged error.")
                raise
            if not self.executable.exists():
                raise RuntimeError(
                    f"New venv not created. Return code: {result.returncode}, Stderr:\n\n{result.stderr}"
                )

    def sync_requirements(
        self, requirements: Literal["infer"] | PathLike | Sequence[PathLike] = "infer"
    ) -> None:
        """Sync libraries based on requirements. Install missing, remove unnecessary.

        Args:
            requirements (Literal["infer"] | PathLike | Sequence[PathLike], optional): Define what libraries
                will be installed. If "infer", autodetected. Can also be a list of more files e.g
                `["requirements.txt", "requirements_dev.txt"]`. Defaults to "infer".
        """
        if requirements == "infer":

            requirements = []

            for i in PROJECT_PATHS.root.glob("*"):
                if "requirements" in i.as_posix().lower() and i.suffix == ".txt":
                    requirements.append(i)  # type: ignore
        else:
            if not isinstance(requirements, list):
                requirements = list(requirements)  # type: ignore

            requirements = [validate_path(req) for req in requirements]

        requirements_content = ""

        for i in requirements:
            with open(i, "r") as req:
                requirements_content = requirements_content + "\n" + req.read()

        # requirements_content = f"{requirements_content}\nmypythontools\npytest"

        requirements_all_path = self.venv_path / "requirements_all.in"
        requirements_all_console_path_str = get_console_str_with_quotes(requirements_all_path)
        freezed_requirements_console_path_str = get_console_str_with_quotes(
            self.venv_path / "requirements.txt"
        )

        with open(requirements_all_path, "w") as requirement_libraries:
            requirement_libraries.write(requirements_content)

        sync_command = (
            f"{self.activate_command} && "
            f"pip install pip-tools && "
            f"pip-compile {requirements_all_console_path_str} --output-file {freezed_requirements_console_path_str} --quiet && "  # pylint: disable="line-too-long"
            f"pip-sync {freezed_requirements_console_path_str} --quiet"
        )

        try:
            result = subprocess.run(sync_command, check=True, shell=True)
            if result.returncode != 0:
                raise RuntimeError

        except (Exception,):
            mylogging.traceback(
                "Update of venv libraries based on requirements failed. Check logged error. Try this command "
                "(if windows, use cmd) with administrator rights in your project root folder because of "
                "permission errors."
                f"\n\n{sync_command}\n\n"
            )
            raise

    def list_packages(self):
        """Get list of installed libraries in the venv. The reason why it's meta coded via string parsing and
        not parsed directly is that it needs to be available from other venv as well."""
        command = (
            """"import pkg_resources"\n"""
            '''"print(sorted([f\'{i.key}=={i.version}\' for i in pkg_resources.working_set]))"'''
        )
        result = subprocess.run(f"{self.executable} -c {command}", capture_output=True)

        output_str = result.stdout.decode().strip("\r\n")

        return literal_eval(output_str)

    def install_library(self, name: str):
        """Install package to venv with pip install."""
        command = f"{self.activate_command} && pip install {name}"
        try:
            result = subprocess.run(command, check=True, shell=True)
            if result.returncode != 0:
                raise RuntimeError
        except Exception:
            raise RuntimeError(mylogging.format_str(f"Library {name} installation failed. Try it manually."))

    def uninstall_library(self, name: str):
        """Uninstall package to venv with pip install."""
        command = f"{self.activate_command} && pip uninstall {name}"
        try:
            result = subprocess.run(command, check=True, shell=True)
            if result.returncode != 0:
                raise RuntimeError
        except Exception:
            raise RuntimeError(mylogging.format_str(f"Library {name} removal failed. Try it manually."))

    def remove(self) -> None:
        """Remove the folder with venv."""
        shutil.rmtree(self.venv_path.as_posix())

    def get_script_path(self, name):
        return get_console_str_with_quotes(self.scripts_path / f"{name}.exe")


def is_venv():
    return sys.base_prefix.startswith(sys.prefix)
