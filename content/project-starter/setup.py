##############
### settings
#############


import SET_YOUR_NAME

author = "Daniel Malachov"  # Change it to your values
author_email = "malachovd@seznam.cz"  # Change it to your values
name = "SET_YOUR_NAME"
url = ("GITHUB_URL",)
short_description = "EDIT_SHORT_DESCRIPTION"
version = SET_YOUR_NAME.__version__  # Edit only app name and keep __version__

# Template suppose you have README.md and requirements.txt in the same folder and version is defined via __version__ in __init__.py


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
    description="Some tools/functions/snippets used across projects.ions.",
    long_description_content_type="text/markdown",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
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
