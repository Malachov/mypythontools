"""Plot data. There is only one main function plot. Check it's documentation for how to use it.
"""

import mylogging
from predictit import misc
from predictit.configuration import Config

# Lazy imports
# from pathlib import Path

# import plotly as pl
# import matplotlib.pyplot as plt
# from IPython import get_ipython


def plot(
    complete_dataframe,
    plot_type="plotly",
    legend=True,
    highlighted_column="",
    surrounded_column="",
    grey_area=False,
    save=False,
    plot_return=False,
    show=True,
):
    """Plots the data. Plotly or matplotlib can be used. It is possible to highlite two columns with different formating.
    It is usually used for time series visualization, but it can be used for different use case of course.

    Examples:

        Just plot dataframe as is

        >>> import predictit
        ...
        >>> predictit.plots.plot(pd.DataFrame([[None, None, 1], [None, None, 2], [3, 3, 6], [3, 2.5, 4]]))

    Args:
        complete_dataframe (pd.DataFrame): Data to be plotted.
        plot_type (str, optional): 'plotly' or 'matplotlib'. Defaults to "plotly".
        legend (bool, optional): Whether display legend or not. Defaults to True.
        highlighted_column (str, optional): Column name that will be formatted differently (blue). Can be empty. Defaults to "".
        surrounded_column (str, optional): Column name that will be formatted differently (black, wider). And is surrounded by
            grey_area. Can be empty (if grey_area is False). Defaults to "".
        grey_area ((bool, list[str])), optional): Whether to show grey area surrounding the surrounded_column. Can be False,
            or list of ['lower_bound_column', 'upper_bound_column']. Both columns has to be in complete_dataframe. Defaults to False.
        save ((False, str), optional): Whether save the plot.  If False or "", do not save, if path as str, save to defined path,
            if "DESKTOP" save to desktop. Defaults to "".
        plot_return ((bool, str), optional): If 'div', return html div with plot as string. If False, just plot and do not return.
            Defaults to False.
        show (bool, optional): Can be evaluated, but not shown (testing reasons). Defaults to True.

    Returns:
        str: Only if plot_return == 'div
    """

    if save == "DESKTOP":

        from pathlib import Path

        save = Path.home() / "Desktop" / "plot.html"

    if plot_type == "matplotlib":
        if misc._JUPYTER:
            from IPython import get_ipython

            get_ipython().run_line_magic("matplotlib", "inline")

        import matplotlib.pyplot as plt

        plt.rcParams["figure.figsize"] = (12, 8)

        complete_dataframe.plot()
        if legend:
            plt.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, 1.05),
                ncol=3,
                fancybox=True,
                shadow=True,
            )

        if save:
            plt.savefig(save)

        if show:
            plt.show()

    elif plot_type == "plotly":

        import plotly as pl

        pl.io.renderers.default = "notebook_connected" if misc._JUPYTER else "browser"
        complete_dataframe = complete_dataframe.copy()
        graph_data = []

        grey_area = 1 if "Upper bound" in complete_dataframe and "Lower bound" in complete_dataframe else 0

        if grey_area:
            upper_bound = pl.graph_objs.Scatter(
                name="Upper bound",
                x=complete_dataframe.index,
                y=complete_dataframe[grey_area[0]],
                line={"width": 0},
            )

            complete_dataframe.drop(grey_area[0], axis=1, inplace=True)
            graph_data.append(upper_bound)

        if surrounded_column:

            if surrounded_column in complete_dataframe.columns:
                best_prediction = pl.graph_objs.Scatter(
                    name="surrounded_column",
                    x=complete_dataframe.index,
                    y=complete_dataframe[surrounded_column],
                    line={"color": "rgb(51, 19, 10)", "width": 5},
                    fillcolor="rgba(68, 68, 68, 0.3)",
                    fill="tonexty" if grey_area else None,
                )

                complete_dataframe.drop(surrounded_column, axis=1, inplace=True)
                graph_data.append(best_prediction)

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
                y=complete_dataframe[grey_area[1]],
                line={"width": 0},
                fillcolor="rgba(68, 68, 68, 0.3)",
                fill="tonexty",
            )

            complete_dataframe.drop(grey_area[1], axis=1, inplace=True)
            graph_data.append(lower_bound)

        if highlighted_column:

            if highlighted_column in complete_dataframe.columns:

                highlighted_column_ax = pl.graph_objs.Scatter(
                    name=str(highlighted_column),
                    x=complete_dataframe.index,
                    y=complete_dataframe[highlighted_column],
                    line={"color": "rgb(31, 119, 180)", "width": 2},
                )

                complete_dataframe.drop(highlighted_column, axis=1, inplace=True)
                graph_data.append(highlighted_column_ax)

            else:
                raise KeyError(
                    mylogging.return_str(
                        r"highlighted_column - {highlighted_column} not found in data columns. Possible columns are: {complete_dataframe.columns}"
                    )
                )

        fig = pl.graph_objs.Figure(data=graph_data)

        for i in complete_dataframe.columns:
            fig.add_trace(pl.graph_objs.Scatter(x=complete_dataframe.index, y=complete_dataframe[i], name=i))

        fig.layout.update(
            yaxis=dict(title="Values"),
            title={
                "text": Config.plot_name,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "y": 0.9 if misc._JUPYTER else 0.95,
            },
            titlefont={"size": 28},
            showlegend=True if legend else False,
            legend_orientation="h",
            hoverlabel={"namelength": -1},
            font={"size": 17},
            margin={"l": 160, "r": 130, "b": 160, "t": 110},
        )

        if show:
            fig.show()

        if save:
            fig.write_html(save)

        if plot_return == "div":

            fig.layout.update(
                title=None,
                height=290,
                paper_bgcolor="#d9f0e8",
                margin={"b": 35, "t": 35, "pad": 4},
            )

            return pl.offline.plot(fig, include_plotlyjs=False, output_type="div")
