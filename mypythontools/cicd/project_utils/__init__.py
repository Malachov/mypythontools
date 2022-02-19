"""
This module can be used for example in running deploy pipelines or githooks
(some code automatically executed before commit). This module can run the tests,
edit library version, generate rst files for docs, push to git or deploy app to pypi.

All of that can be done with one function call - with `project_utils_pipeline` function that
run other functions, or you can use functions separately. 


Examples:
=========

    **VS Code Task example**

    You can push changes with single click with all the hooks displaying results in
    your terminal. All params changing every push (like git message or tag) can
    be configured on the beginning and therefore you don't need to wait for test finish.
    Default values can be also used, so in small starting projects, push is actually very fast.

    Create folder utils, create `push_script.py` inside, add::

        from mypythontools import cicd

        if __name__ == "__main__":
            # Params that are always the same define here. Params that are changing define in IDE when run action.
            # For example in tasks (command line arguments and argparse will be used).
            cicd.project_utils.project_utils_pipeline(deploy=True)

    Then just add this task to global tasks.json::

        {
          "version": "2.0.0",
          "tasks": [
            {
              "label": "Build app",
              "type": "shell",
              "command": "python",
              "args": ["${workspaceFolder}/utils/build_script.py"],
              "presentation": {
                "reveal": "always",
                "panel": "new"
              }
            },
            {
              "label": "Push to PyPi",
              "type": "shell",
              "command": "python",
                "args": [
                  "${workspaceFolder}/utils/push_script.py",
                  "--deploy",
                  "True",
                  "--test",
                  "False",
                  "--reformat",
                  "False",
                  "--version",
                  "--commit_and_push_git",
                  "False",
                  "--sphinx_docs",
                  "False"
                ],
                "presentation": {
                  "reveal": "always",
                  "panel": "new"
              }
            },
            {
              "label": "Hooks & push & deploy",
              "type": "shell",
              "command": "python",
              "args": [
                "${workspaceFolder}/utils/push_script.py",
                "--version",
                "${input:version}",
                "--commit_message",
                "${input:commit_message}",
                "--tag",
                "${input:tag}",
                "--tag_mesage",
                "${input:tag-message}"
              ],
              "presentation": {
                "reveal": "always",
                "panel": "new"
              }
            }
          ],
          "inputs": [
            {
              "type": "promptString",
              "id": "version",
              "description": "Version in __init__.py will be overwiten. Version has to be in format like '1.0.3' three digits and two dots. If None, nothing will happen. If 'increment', than it will be updated by 0.0.1.",
              "default": "increment"
            },
            {
              "type": "promptString",
              "id": "commit_message",
              "description": "Git message for commit.",
              "default": "New commit"
            },
            {
              "type": "promptString",
              "id": "tag",
              "description": "Git tag. If '__version__' is used, then tag from version in __init__.py will be derived. E.g. 'v1.0.1' from '1.0.1'",
              "default": "__version__"
            },
            {
              "type": "promptString",
              "id": "tag-message",
              "description": "Git tag message.",
              "default": "New version"
            }
          ]
        }


    **Git hooks example**

    Create folder git_hooks with git hook file - for pre commit name must be `pre-commit`
    (with no extension). Hooks in git folder are gitignored by default (and hooks is not visible
    on first sight).

    Then add hook to git settings - run in terminal (last arg is path (created folder))::

        $ git config core.hooksPath git_hooks

    In created folder on first two lines copy this::

        #!/usr/bin/env python
        # -*- coding: UTF-8 -*-

    Then just import any function from here and call with desired params. E.g.
"""
from mypythontools.cicd.project_utils.project_utils_pipeline_internal import project_utils_pipeline
from mypythontools.cicd.project_utils import project_utils_functions

__all__ = ["project_utils_pipeline", "project_utils_functions"]
