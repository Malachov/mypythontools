from typing_extensions import Literal

##############
### settings
#############

# Template suppose you have README.md and requirements.txt in the same folder and version is defined via __version__ in __init__.py

import SET_YOUR_NAME

author = "Daniel Malachov"  # Change it to your values
author_email = "malachovd@seznam.cz"  # Change it to your values
development_status: Literal["3 - Alpha", "4 - Beta", "5 - Production/Stable"] = "4 - Beta"
documentation_url = "https://readthedocs.org/projects/yourproject"
home_url = "https://github.com/user/project"
keywords: list = []
name: str = "SET_YOUR_NAME"
short_description = "EDIT_SHORT_DESCRIPTION"
url = "GITHUB_URL"
version = SET_YOUR_NAME.__version__  # Edit only app name and keep __version__


#####################
### End of settings
####################

# Usually no need of editting further


from setuptools import setup, find_packages
import pkg_resources

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    my_requirements = [str(requirement) for requirement in pkg_resources.parse_requirements(f)]

setup(
    author_email=author_email,
    author=author,
    description=short_description,
    extras_require={},
    include_package_data=True,
    install_requires=my_requirements,
    keywords=keywords,
    license="mit",
    long_description_content_type="text/markdown",
    long_description=readme,
    name=name,
    packages=[name],
    platforms="any",
    project_urls={
        "Documentation": documentation_url,
        "Home": home_url,
    },
    url=url,
    version=version,
    classifiers=[
        f"Development Status :: {development_status}",
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
