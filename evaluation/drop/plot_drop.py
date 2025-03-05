"""
Build graph for finding the limit of pps forwaded
by the Linux kernel before packet drop.
"""

import pandas as pd
import os
import sys

# include generic plotting
sys.path.append("..")
from GenericPlotting import *

# Folders containing raw data

def load_data(folder : str, file : str, separator : str):
    """Load `file` in `folder`. `separator` used to separate columns in csv."""
    df = pd.read_csv(os.path.join(folder, file), sep=separator, header=None)
    df.rename(columns={0: "pps", 1: "rx_pps", 2: "tx_pps", 3: "ipackets", 4: "opackets", 5:"dropRate"}, inplace=True)
    return df

def plot():
    """Build plot."""

    data = load_data(".", "drop.txt", ";")

    # compute means by value of pps
    dataAggregated = data.groupby(data['pps']).mean()
    del dataAggregated['rx_pps']
    del dataAggregated['tx_pps']
    del dataAggregated['ipackets']
    del dataAggregated['opackets']

    # compute stddevs
    mtuStd = (data.groupby(data['pps']).std())['dropRate'].values

    # put everything in single dataframe
    aggregated = dataAggregated.copy(deep=True)
    aggregated.rename(columns={"dropRate": "Drop Rate"}, inplace=True)

    # convert pps to mpps
    aggregated.index/=10**6

    # insert stddevs
    aggregated.insert(1, "STD", mtuStd)
    print(aggregated)

    # plot
    p = GenericPlot()
    dict_line = {
        'legend':['Drop Rate'], 'position_legend':'above',
        'xlabel':'mpps', 'ylabel':'Drop Rate',
        'columns': ['Drop Rate'], 'xval': 'pps',
        'yerr': ['STD'], 'shaded_color': ['tab:blue'],
        'grid':True, 'linewidth': 2,
        'markers': ['.', 'd', '^'],
        'dpoints': True, 'marker_size': 5,
        'y_lim': [-0.001, 0.05]
    }
    fig, ax = p.generic_plot(Plot.LINE_PLOT_CI, aggregated, dict_parameters=dict_line)

    # modify xaxis
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.02))
    ax.set_xticks(ax.get_xticks(), ax.get_xticklabels())
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.01))

    fig.set_figheight(3)
    fig.set_figwidth(6)

    # save plot
    fig.savefig("drop.pdf", bbox_inches='tight')

if __name__ == "__main__":
    plot()
