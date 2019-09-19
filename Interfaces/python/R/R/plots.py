import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys


def pretty_plot_ticks(low, high, n):
    """Return a set of 'pretty' tick labels.

    Args:
      low: The lower end of the plotting range.
      high: The upper end of the plotting range.
      n: The desired number of ticks.

    Returns:
      A np.array with 'pretty' values suitable for tick labels.  The length of
      the array will typically not be exactly 'n'.  Its lower endpoint will be
      <= low and its upper endpoint will be >= high.

    Taken from StackOverflow:
    https://stackoverflow.com/questions/43075617/python-function-equivalent-to-rs-pretty

    """
    def nicenumber(x, round):
        exp = np.floor(np.log10(x))
        f = x / 10**exp

        if round:
            if f < 1.5:
                nf = 1.
            elif f < 3.:
                nf = 2.
            elif f < 7.:
                nf = 5.
            else:
                nf = 10.
        else:
            if f <= 1.:
                nf = 1.
            elif f <= 2.:
                nf = 2.
            elif f <= 5.:
                nf = 5.
            else:
                nf = 10.

        return nf * 10.**exp

    range = nicenumber(high - low, False)
    d = nicenumber(range / (n - 1), True)
    miny = np.floor(low / d) * d
    maxy = np.ceil(high / d) * d
    return np.arange(miny, maxy+0.5*d, d)


def plot_dynamic_distribution(
        curves,
        timestamps=None,
        quantile_step=.1,
        xlim=None,
        ylim=None,
        xlab="Time",
        ylab="distribution",
        col="black",
        ax=None,
        show=True,
        **kwargs):
    """Plot a dynamic distribution represented by a collection of curves simulated
    from that distribution.

    Args:
      curves:
        A numpy matrix of time series.  Rows correspond to different series,
        and columns correspond to time.

      timestamps:
        An array-like collection of increasing time stamps corresponding to the
        time points in 'curves.'

      quantile_step:
        The plotted distribution is formed by taking the quantiles of the
        curves at each time point.  The smaller the value of quantile_step the
        finer the approximation, but the larger and slower the plot.

      xlim:
        The limits on the horizontal axis.

      xlab:
        The label for the horizontal axis.

      ylim: the y limits (y1, y2) of the plot.
      ylab: Label for the vertical axis.
      **kwargs: Extra arguments passed to .... ???

    """

    if ax is None:
        fig, ax = plt.subplots(1, 1, **kwargs)

    quantile_points = np.arange(0, 1, quantile_step)
    curve_quantiles = np.quantile(curves, q=quantile_points, axis=0)
    if timestamps is None:
        timestamps = np.arange(curves.shape[1])
    assert(len(timestamps) == curves.shape[1])

    for i in range(int(np.floor(len(quantile_points) / 2))):
        lo = curve_quantiles[i, :]
        hi = curve_quantiles[-1-i, :]
        ax.fill_between(timestamps, lo, hi,
                        color=col,
                        facecolor="none",
                        edgecolor="none",
                        lw=.0000,
                        alpha=(i / len(quantile_points)))

    if xlim is not None:
        ax.set_xlim(xlim)

    if ylim is not None:
        ax.set_ylim(ylim)

    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    if show:
        fig.show()

    return ax


def hl2(actual, predicted, ax=None, **kwargs):
    fig = None
    if ax is None:
        fig, ax = plt.subplots(1, 1, **kwargs)
    group_means = pd.DataFrame({"pred": predicted, "actual": actual}).groupby(
        pd.qcut(predicted, 10))["actual"].mean()


def hosmer_lemeshow_plot(actual, predicted, ax=None, **kwargs):
    """Construct a Hosmer Lemeshow plot on the supplied axes.  A Hosmer Lemeshow
    plot partitions the predicted values into groups, and compares the
    midpoint of each group with the observed proportion in the group.

    Args:
      actual: The actual set of 0's and 1's being modeled.
      predicted: The predicted probabilities coresponding to 'actual'.
      ax: The pyplot axes on which to draw the plot, or None.  If None the
        figure will be shown on function exit.
      **kwargs: Passed to plt.subplots in the event that ax is None.

    Return:
      fig: If a new figure was created then this is the containing object.
        Otherwise None.
      ax: The axes object containing the plot.

    """
    fig = None
    if ax is None:
        fig, ax = plt.subplots(1, 1, **kwargs)
    group_means = pd.DataFrame({"pred": predicted, "actual": actual}).groupby(
        pd.qcut(predicted, 10))["actual"].mean()
    bar_locations = group_means.index.categories.mid.values
    lower = np.array([x.left for x in group_means.index.values])
    upper = np.array([x.right for x in group_means.index.values])
    bar_widths = .8 * (upper - lower)

    ax.barh(bar_locations, group_means, height=bar_widths)
    ax.set_xticks(bar_locations)
    labels = [str(lab) for lab in group_means.index.values]
    ax.set_yticklabels(labels)
    ax.set_ylabel("Predicted Proportions")

    xticks = pretty_plot_ticks(np.min(predicted), np.max(predicted), 5)
    ax.set_xticks(xticks)
    ax.set_xlabel("Observed Proportions")

    if fig is not None:
        fig.show()
    return fig, ax