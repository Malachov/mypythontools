"""Module with functions for 'venvs' subpackage."""

from __future__ import annotations
import platform
import subprocess
from pathlib import Path
import shutil

import mylogging

from ...helpers import paths
from ...helpers.misc import misc


class Venv:
    """You can create new venv or sync it's dependencies.

    Example:
        >>> venv = Venv("venv")
        >>> venv.create()
        >>> venv.sync_requirements()
    """

    def __init__(self, venv_path: Path | str) -> None:

        self.venv_path = Path(venv_path)
        self.venv_path_console_str = misc.get_console_str_with_quotes(self.venv_path)

        if not self.venv_path.exists():
            self.venv_path.mkdir(parents=True, exist_ok=True)

        if platform.system() == "Windows":
            activate_path = self.venv_path / "Scripts" / "activate.bat"
            self.exists = True if activate_path.exists() else False
            self.create_command = f"python -m venv {self.venv_path_console_str}"
            self.activate_command = misc.get_console_str_with_quotes(activate_path)
        else:
            self.exists = True if (self.venv_path / "bin").exists() else False
            self.create_command = f"python3 -m virtualenv {self.venv_path_console_str}"
            self.activate_command = (
                f"source {misc.get_console_str_with_quotes(self.venv_path / 'bin' / 'activate')}"
            )
        # self.deactivate_command = "TODO"

    def create(
        self,
    ) -> None:
        """Create virtual environment. If it already exists, it will be skipped and nothing happens."""

        if not self.exists:
            try:
                if platform.system() == "Windows":
                    subprocess.run(self.create_command, check=True)
                else:
                    subprocess.run(self.create_command, check=True)
            except (Exception,):
                mylogging.traceback("Creation of venv failed. Check logged error.")
                raise

    def sync_requirements(self, requirements: str | Path | list[str] | list[Path] = "infer") -> None:
        """Sync libraries based on requirements. Install missing, remove unnecessary.

        Args:
            requirements (str | Path | list[str] | list[Path], optional): Define what libraries will be
                installed. If "infer", autodetected. Can also be a list of more files e.g
                `["requirements.txt", "requirements_dev.txt"]`. Defaults to "infer".
        """
        if requirements == "infer":

            requirements = []

            for i in paths.PROJECT_PATHS.root.glob("*"):
                if "requirements" in i.as_posix().lower() and i.suffix == ".txt":
                    requirements.append(i)  # type: ignore
        else:
            if not isinstance(requirements, list):
                requirements = list(requirements)  # type: ignore

            requirements = [paths.validate_path(req) for req in requirements]

        requirements_content = ""

        for i in requirements:
            with open(i, "r") as req:
                requirements_content = requirements_content + "\n" + req.read()

        requirements_content = f"{requirements_content}\nmypythontools\npytest"

        requirements_all_path = self.venv_path / "requirements_all.in"
        requirements_all_console_path_str = misc.get_console_str_with_quotes(requirements_all_path)
        freezed_requirements_console_path_str = misc.get_console_str_with_quotes(
            self.venv_path / "requirements.txt"
        )

        with open(requirements_all_path, "w") as requirement_libraries:
            requirement_libraries.write(requirements_content)

        requirements_command = (
            "pip install pip-tools && "
            f"pip-compile {requirements_all_console_path_str} --output-file {freezed_requirements_console_path_str}  --quiet && "  # pylint: disable="line-too-long"
            f"pip-sync {freezed_requirements_console_path_str} --quiet"
        )

        sync_command = f"{self.activate_command} && {requirements_command}"

        try:
            subprocess.run(sync_command, check=True, shell=True)
        except (Exception,):
            mylogging.traceback(
                "Update of venv libraries based on requirements failed. Check logged error. Try this command "
                "(if windows, use cmd) with administrator rights in your project root folder because of "
                "permission errors."
                f"\n\n{sync_command}\n\n"
            )
            raise

    def remove(self) -> None:
        """Remove the folder with venv."""
        shutil.rmtree(self.venv_path.as_posix())
