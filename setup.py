from setuptools import setup, find_packages
import pkg_resources
import mypythontools

version = mypythontools.__version__

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    my_requirements = [str(requirement) for requirement in pkg_resources.parse_requirements(f)]

if __name__ == "__main__":

    setup(
        author_email="malachovd@seznam.cz",
        author="Daniel Malachov",
        description="Some tools/functions/snippets used across projects.",
        include_package_data=True,
        install_requires=my_requirements,
        # extras_require={},
        license="mit",
        long_description_content_type="text/markdown",
        long_description=readme,
        name="mypythontools",
        packages=find_packages(exclude=("tests**",)),
        platforms="any",
        project_urls={
            "Documentation": "https://mypythontools.readthedocs.io/",
            "Homepage": "https://github.com/Malachov/mypythontools",
        },
        python_requires=">=3.7",
        url="https://github.com/Malachov/mypythontools",
        version=version,
        entry_points={
            "console_scripts": [
                "mypythontools.cicd = mypythontools.cicd.project_utils:project_utils_pipeline",
            ],
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
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
