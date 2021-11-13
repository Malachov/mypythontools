##############
### settings
#############

# Template suppose you have README.md and requirements.txt in the same folder and version is defined via __version__ in __init__.py

import SET_YOUR_NAME

author = "Daniel Malachov"  # Change it to your values
author_email = "malachovd@seznam.cz"  # Change it to your values
name = "SET_YOUR_NAME"
url = ("GITHUB_URL",)
short_description = "EDIT_SHORT_DESCRIPTION"
version = SET_YOUR_NAME.__version__  # Edit only app name and keep __version__
keywords = []

# Check if classifiers OK. Reference here: https://gist.github.com/nazrulworld/3800c84e28dc464b2b30cec8bc1287fc
development_status = "3 - Alpha"


#####################
### End of settings
####################

# No need of editting further


from setuptools import setup, find_packages
import pkg_resources

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    myreqs = [str(requirement) for requirement in pkg_resources.parse_requirements(f)]

setup(
    name=name,
    version=version,
    url=url,
    license="mit",
    author=author,
    author_email=author_email,
    install_requires=myreqs,
    description=short_description,
    long_description_content_type="text/markdown",
    long_description=readme,
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    platforms="any",
    keywords=keywords,
    classifiers=[
        "Programming Language :: Python",
        f"Development Status :: {development_status}",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
        "Environment :: Other Environment",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
    ],
    extras_require={},
)
