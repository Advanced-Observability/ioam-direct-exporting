"""
Build graphs for encapsulating node.
"""

import os
import sys
import pandas
import numpy as np
import scipy.stats as st
import re

# include generic plotting
sys.path.append("../")
from GenericPlotting import *

FREQUENCIES = [10**-5, 10**-4, 10**-3, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
FREQUENCIES_STR = ['0.001', '0.01', '0.1', '1', '5', '10', '25', '50', '100']

LS = [':', '--', '-.', ':', '--', '-.', ':', '--', '-.', ':', '--']
MARKERS = ['.', 'v', '*', 's', 'x', 'p', '+', 'D', 'p', '1', '^']

DATA_FIELDS = [
    "0x800000", "0x400000", "0x200000", "0x100000",
    "0x40000", "0x20000",
    "0x8000", "0x4000", "0x2000"
]

BASELINE = 1070000

def parse_file(filename : str, separator : str):
    """Parse CSV data in `filename` using `separator` to split columns."""

    f = open(filename, "r")
    df = pandas.read_csv(f, sep=separator, header=None)
    f.close()

    del df[df.columns[0]]
    df.rename(columns={1: "pps", 2: "bps", 3: "ipackets", 4: "opackets"}, inplace=True)

    df['pps']/=10**5

    mean = np.mean(df["pps"])
    var = np.var(df["pps"])
    stddev = np.std(df["pps"])

    # 95% confidence interval student-t on mean
    interval = st.t.interval(0.95, df=len(df["pps"])-1, loc=np.mean(df["pps"]), scale=st.sem(df["pps"]))

    return mean, var, stddev, interval

def extract_directory(dirPath: str) -> dict:
    "Extract all data from all files in directory `dirPath`."

    # get list of files
    files = os.listdir(dirPath)
    files = [f for f in files if f.endswith("_stats.txt")]
    files.sort()

    data = {}

    # load and parse data
    for f in files:
        parsed = parse_file(os.path.join(dirPath, f), ";")

        percentages = re.search(r'\d+_\d+_stats', f).group(0)
        percentages = re.search(r'\d+_\d+', percentages).group(0).split("_")
        freq = float(percentages[1]) / float((int(percentages[0]) + int(percentages[1])))

        mode = re.search(r"0x\d+", f).group(0)

        data[f] = (mode, freq, parsed)

    return data

def build_dataframe(data: dict) -> pandas.DataFrame:
    """Build dataframe from dictionary `data`."""

    df = pd.DataFrame(0.0, index=FREQUENCIES_STR, columns=DATA_FIELDS)
    df.index.name = "Frequency"
    inter = pd.DataFrame(0.0, index=FREQUENCIES_STR, columns=DATA_FIELDS)
    inter.index.name = "Frequency"

    for d in data:
        d = data[d]
        #interval = d[2][3][1] - d[2][3][0]
        interval = d[2][2]
        x = FREQUENCIES.index(d[1])
        y = DATA_FIELDS.index(d[0])
        inter.iat[x,y] = interval
        df.iat[x, y] = d[2][0]

    return df, inter

def plot(df: pandas.DataFrame, inter: pandas.DataFrame, plotFile: str):
    """Plot data stored inside `df` and store plot in `plotFile`."""

    ylabel = r'pps received ($10^5$)'
    ylim = [0, 14]
    legendPos = "lower center"

    df.columns = [
        "HopLim+ID", "Ingress+Egress", "Timestamp", "TimestampFraction",
        "NamespaceSpecific", "QueueDepth",
        "HopLim+ID(wide)", "Ingress+Egress(wide)", "NamespaceSpecific(wide)"
    ]

    p = GenericPlot()
    dict_line = {
        'xlabel':'Injection rate (in \%)', 'ylabel': ylabel,
        'yerr': inter.transpose().values,
        'marker': MARKERS,
        'marker_size': 3,
        'my_ls': LS,
        'legend': DATA_FIELDS, 'position_legend': legendPos,
        'grid':True,
        'columns': df.columns,
        'linewidth': 1,
        'y_lim': ylim,
    }

    fig, ax = p.generic_plot(Plot.LINE_PLOT_CI, df, dict_parameters=dict_line)
    ax.hlines(BASELINE/10**5, 0, 8, linestyles='solid', linewidth=1, colors=['red'], label='Baseline')

    plt.legend(ncol=2, loc=legendPos)

    ax.set_xticks(ticks=range(len(FREQUENCIES_STR)), labels=FREQUENCIES_STR, horizontalalignment='center')

    ax.set_yticks(range(0, 14, 2))
    ax.set_ylim([0, 12])

    fig.set_figheight(3)
    fig.set_figwidth(6)

    fig.savefig(plotFile, bbox_inches='tight')

def plot_data():
    print("\n\n~ Data fields ~\n\n")

    dir = "data/data"
    filenamePrefix = "encap_data"

    data = extract_directory(dir)

    df, inter = build_dataframe(data)
    df.to_csv(f"{filenamePrefix}.csv")

    plot(df, inter, f"{filenamePrefix}.pdf")

if __name__ == "__main__":
    plot_data()
