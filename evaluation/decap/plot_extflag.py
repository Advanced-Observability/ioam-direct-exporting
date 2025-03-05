"""
Build graphs for decapsulating node.
"""

import os
import sys
import pandas as pd
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

EXT_FLAGS = ["NO_EXT", "FLOW", "FLOW_SEQ"]

BASELINE = 1070000

def parse_file(filename : str, separator : str):
    """Parse CSV data in `filename` using `separator` to split columns."""

    f = open(filename, "r")
    df = pd.read_csv(f, sep=separator, header=None)
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
    fileList = os.listdir(dirPath)

    filesNoExt = [f for f in fileList if f.endswith("_stats.txt") and "NO_EXT" in f and "800000" in f]
    filesFlowOnly = [f for f in fileList if f.endswith("_stats.txt") and "FLOW" in f and "SEQ" not in  f]
    filesFlowSeq = [f for f in fileList if f.endswith("_stats.txt") and "FLOW_SEQ" in f]

    files = [*filesNoExt, *filesFlowOnly, *filesFlowSeq]

    data = {}

    # load and parse data
    for f in files:
        parsed = parse_file(os.path.join(dirPath, f), ";")

        percentages = re.search(r'\d+_\d+_stats', f).group(0)
        percentages = re.search(r'\d+_\d+', percentages).group(0).split("_")
        freq = float(percentages[1]) / float((int(percentages[0]) + int(percentages[1])))

        if f in filesNoExt:
            extflag = "NO_EXT"
        elif f in filesFlowOnly:
            extflag = "FLOW"
        elif f in filesFlowSeq:
            extflag = "FLOW_SEQ"

        data[f] = (extflag, freq, parsed)

    return data

def build_dataframe(data: dict) -> pd.DataFrame:
    """Build dataframe from dictionary `data`."""

    df = pd.DataFrame(0.0, index=FREQUENCIES_STR, columns=EXT_FLAGS)
    df.index.name = "Frequency"
    inter = pd.DataFrame(0.0, index=FREQUENCIES_STR, columns=EXT_FLAGS)
    inter.index.name = "Frequency"

    for d in data:
        d = data[d]
        #interval = d[2][3][1] - d[2][3][0]
        interval = d[2][2]
        x = FREQUENCIES.index(d[1])
        y = EXT_FLAGS.index(d[0])
        inter.iat[x,y] = interval
        df.iat[x, y] = d[2][0]

    return df, inter

def plot(df: pd.DataFrame, inter: pd.DataFrame, plotFile: str):
    """Plot data stored inside `df` and store plot in `plotFile`."""

    ylabel = r'pps received ($10^5$)'
    ylim = [0, 14]
    legendPos = "lower center"

    df.columns = ["None", "Flow ID", "Flow ID \& Seq Num"]

    p = GenericPlot()
    dict_line = {
        'xlabel':'Injection rate (in \%)', 'ylabel': ylabel,
        'yerr': inter.transpose().values,
        'marker': MARKERS,
        'marker_size': 3,
        'my_ls': LS,
        'legend': EXT_FLAGS, 'position_legend': legendPos,
        'grid':True,
        'columns': df.columns,
        'linewidth': 1,
        'y_lim': ylim,
    }

    fig, ax = p.generic_plot(Plot.LINE_PLOT_CI, df, dict_parameters=dict_line)
    ax.hlines(BASELINE/10**5, 0, 8, linestyles='solid', linewidth=1, colors=['red'], label='Baseline')

    plt.legend(ncol=4, loc=legendPos)

    ax.set_xticks(ticks=range(len(FREQUENCIES_STR)), labels=FREQUENCIES_STR, horizontalalignment='center')

    ax.set_yticks(range(0, 14, 2))
    ax.set_ylim([0, 12])

    fig.set_figheight(3)
    fig.set_figwidth(6)

    fig.savefig(plotFile, bbox_inches='tight')

def plot_extflag():
    print("\n\n~ Extension Flags ~\n\n")

    dir = "data"
    filenamePrefix = "dacap_extflag"

    data = extract_directory(dir)

    df, inter = build_dataframe(data)
    df.to_csv(f"{filenamePrefix}.csv")

    plot(df, inter, f"{filenamePrefix}.pdf")

if __name__ == "__main__":
    plot_extflag()
