"""Install the package."""
from setuptools import setup, find_packages
import pkg_resources
import re

if __name__ == "__main__":

    with open("pyvueeel/__init__.py") as version_file:
        version = re.findall('__version__ = "(.*)"', version_file.read())[0]

    with open("README.md") as readme_file:
        readme = readme_file.read()

    with open("requirements.txt") as f:
        my_requirements = [str(requirement) for requirement in pkg_resources.parse_requirements(f)]

    development_status = "3 - Alpha"  # 4 - Beta, 5 - Production/Stable

    setup(
        name="pyvueeel",
        author_email="malachovd@seznam.cz",
        author="Daniel Malachov",
        description="Some tools/functions/snippets used across projects.",
        project_urls={
            "Documentation": "https://pyvueeel.readthedocs.io/",
            "Homepage": "https://github.com/Malachov/pyvueeel",
        },
        url="https://github.com/Malachov/pyvueeel",
        python_requires=">=3.7",
        ##############################
        ## Further usually not changed
        ##############################
        include_package_data=True,
        install_requires=my_requirements,
        # extras_require={},
        license="mit",
        long_description_content_type="text/markdown",
        long_description=readme,
        packages=find_packages(exclude=("tests**",)),
        platforms="any",
        version=version,
        classifiers=[
            f"Development Status :: {development_status}",
            # "Development Status :: 4 - Beta
            # "Development Status :: 5 - Production/Stable",
            "Environment :: Other Environment",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Application Frameworks",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    )
