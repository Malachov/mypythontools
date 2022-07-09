"""Install the package."""

from setuptools import setup

from mypythontools_cicd import packages

if __name__ == "__main__":

    extras_requirements = {
        i: packages.get_requirements(f"requirements/requirements_extras_{i}.txt") for i in ["plots"]
    }

    setup(
        description="Some tools/functions/snippets used across projects.",
        long_description=packages.get_readme(),
        install_requires=packages.get_requirements("requirements/requirements.txt"),
        extras_require=extras_requirements,
        entry_points={
            "console_scripts": [
                "mypythontools_cicd = mypythontools_cicd.cicd:cicd_pipeline",
            ],
        },
        **packages.get_package_setup_args("mypythontools_cicd", development_status="alpha"),
        **packages.personal_setup_args_preset,
    )
