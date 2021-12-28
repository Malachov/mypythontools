"""Plot data. There is only one main function plot. Check it's documentation for how to use it."""

from __future__ import annotations
from typing import cast
from pathlib import Path
from dataclasses import dataclass

from typing_extensions import Literal

import mylogging

from . import misc
from . import paths

# Lazy imports
# from pathlib import Path

# import plotly as pl
# import matplotlib.pyplot as plt
# from IPython import get_ipython


class GetPlotlyLayouts:
    """Plotly layouts. Use `fig.layout.update(get_plotly_layout.categorical_scatter(title="My title"))'"""

    def general(self, title):
        return {
            "title": {
                "text": title,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "y": 0.9 if misc.JUPYTER else 0.95,
            },
            "titlefont": {"size": 28},
            "font": {"size": 17},
        }

    def categorical_scatter(self, title):
        return {
            **self.general(title),
            "margin": {"l": 320, "r": 150, "b": 180, "t": 130},
            "titlefont": {"size": 34},
            "font": {"size": 22},
            "yaxis": {"tickfont": {"size": 18}, "ticksuffix": " ", "title": {"standoff": 20}},
        }

    def time_series(self, title, showlegend, yaxis="Values"):
        return {
            **self.general(title),
            "yaxis": {"title": yaxis},
            "showlegend": showlegend,
            "legend_orientation": "h",
            "hoverlabel": {"namelength": -1},
            "margin": {"l": 160, "r": 130, "b": 160, "t": 110},
        }


get_plotly_layout = GetPlotlyLayouts()


def plot(
    complete_dataframe,
    plot_library: Literal["plotly", "matplotlib"] = "plotly",
    title: str = "Plot",
    legend: bool = True,
    y_axis_name="Values",
    highlighted_column="",
    surrounded_column="",
    grey_area: None | list[str] = None,
    save: None | Path | str = None,
    return_div: bool = False,
    show: bool = True,
) -> None | str:
    """Plots the data. Plotly or matplotlib can be used. It is possible to highlite two columns with different formating.
    It is usually used for time series visualization, but it can be used for different use case of course.

    Args:
        complete_dataframe (pd.DataFrame): Data to be plotted.
        plot_library (Literal['plotly', 'matplotlib'], optional): 'plotly' or 'matplotlib'. Defaults to "plotly".
        legend (bool, optional): Whether display legend or not. Defaults to True.
        highlighted_column (str, optional): Column name that will be formatted differently (blue). Can be empty. Defaults to "".
        surrounded_column (str, optional): Column name that will be formatted differently (black, wider). And is surrounded by
            grey_area. Can be empty (if grey_area is None). Defaults to "".
        grey_area (None | list[str]), optional): Whether to show grey area surrounding the surrounded_column. Can be None,
            or list of ['lower_bound_column', 'upper_bound_column']. Both columns has to be in complete_dataframe. Defaults to None.
        save (None | Path | str, optional): Whether save the plot.  If False or "", do not save, if Path as str path, save to defined path.
            If "DESKTOP" save to desktop. Defaults to None.
        return_div (bool, optional): If True, return html div with plot as string. If False, just plot and do not return.
            Defaults to False.
        show (bool, optional): Can be evaluated, but not shown (testing reasons). Defaults to True.

    Returns:
        None | str: Only if return_div is True, else None.

    Examples:
        Plot dataframe with

        >>> import pandas as pd
        >>> df = pd.DataFrame([[None, None, 1], [None, None, 2], [3, 3, 6], [3, 2.5, 4]])
        >>> plot(df, show=False)  # Show False just for testing reasons

        You can use matplotlib

        >>> plot(df, plot_library="matplotlib")
    """

    if save == "DESKTOP":
        save = paths.get_desktop_path() / "plot.html"

    if plot_library == "matplotlib":
        if misc.JUPYTER:
            from IPython import get_ipython

            get_ipython().run_line_magic("matplotlib", "inline")

        import matplotlib.pyplot as plt

        plt.rcParams["figure.figsize"] = (12, 8)

        complete_dataframe.plot()
        if legend:
            plt.legend(
                loc="upper center", bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=True,
            )

        if save:
            plt.savefig(save)

        if show:
            plt.show()

    elif plot_library == "plotly":

        import plotly as pl

        pl.io.renderers.default = "notebook_connected" if misc.JUPYTER else "browser"

        used_columns = list(complete_dataframe.columns)

        graph_data = []

        if grey_area:
            grey_area = cast(list, grey_area)

            lower_bound_column = grey_area[0]
            upper_bound_column = grey_area[1]

            upper_bound = pl.graph_objs.Scatter(
                name="Upper bound",
                x=complete_dataframe.index,
                y=complete_dataframe[upper_bound_column],
                line={"width": 0},
            )

            used_columns.remove(upper_bound_column)
            graph_data.append(upper_bound)

        if surrounded_column:

            if surrounded_column in complete_dataframe.columns:
                surrounded = pl.graph_objs.Scatter(
                    name=surrounded_column,
                    x=complete_dataframe.index,
                    y=complete_dataframe[surrounded_column],
                    line={"color": "rgb(51, 19, 10)", "width": 5,},
                    fillcolor="rgba(68, 68, 68, 0.3)",
                    fill="tonexty" if grey_area else None,
                )

                used_columns.remove(surrounded_column)
                graph_data.append(surrounded)

            else:
                raise KeyError(
                    mylogging.return_str(
                        r"surrounded_column - {surrounded_column} not found in data columns. Possible columns are: {complete_dataframe.columns}"
                    )
                )

        if grey_area:
            lower_bound = pl.graph_objs.Scatter(
                name="Lower bound",
                x=complete_dataframe.index,
                y=complete_dataframe[lower_bound_column],
                line={"width": 0},
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty",
            )

            used_columns.remove(lower_bound_column)
            graph_data.append(lower_bound)

        if highlighted_column:

            if highlighted_column in complete_dataframe.columns:

                highlighted_column_ax = pl.graph_objs.Scatter(
                    name=str(highlighted_column),
                    x=complete_dataframe.index,
                    y=complete_dataframe[highlighted_column],
                    line={"color": "rgb(31, 119, 180)", "width": 2,},
                )

                used_columns.remove(highlighted_column)
                graph_data.append(highlighted_column_ax)

            else:
                raise KeyError(
                    mylogging.return_str(
                        r"highlighted_column - {highlighted_column} not found in data columns. Possible columns are: {complete_dataframe.columns}"
                    )
                )

        fig = pl.graph_objs.Figure(data=graph_data)

        for i in complete_dataframe.columns:
            if i in used_columns:

                # Can be multiindex
                name = " - ".join([str(j) for j in i]) if isinstance(i, tuple) else i

                fig.add_trace(
                    pl.graph_objs.Scatter(x=complete_dataframe.index, y=complete_dataframe[i], name=name)
                )

        fig.layout.update(get_plotly_layout.time_series(title, legend, y_axis_name))

        if show:
            fig.show()

        if save:
            fig.write_html(save)

        if return_div:

            fig.layout.update(
                title=None, height=290, paper_bgcolor="#d9f0e8", margin={"b": 35, "t": 35, "pad": 4},
            )

            return pl.offline.plot(fig, include_plotlyjs=False, output_type="div",)
