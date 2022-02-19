# from __future__ import annotations
# from typing import NamedTuple, Any
# from typing_extensions import Literal
# import sys
# from pathlib import Path

# import line_profiler
# import memory_profiler
# import numpy as np
# import pandas as pd

# root_path = Path(__file__).parents[1].as_posix()  # pylint: disable=no-member
# sys.path.insert(0, root_path)

# from mypythontools import cicd


# import mylogging
# from mypythontools.cicd import tests
# import mydatapreprocessing

# tests.setup_tests()


# ##############################

# profile = line_profiler.LineProfiler()  # memory
# # profile = memory_profiler.profile  # time

# ##############################


# # This profiled function is to be profiled from jupyter
# def profiled():
#     pass
#     # array = np.random.randn(100000, 6) + 8 * 6
#     # df = pd.DataFrame(array)

#     # Profiled code here


# if __name__ == "__main__":

#     # (precision=8)  # Just memory profiler
#     @profile
#     def profile_here():
#         pass
#         # array = np.random.randn(100000, 6) + 8 * 6
#         # df = pd.DataFrame(array)

#     profile_here()

#     if hasattr(profile, "print_stats"):
#         profile.print_stats()
