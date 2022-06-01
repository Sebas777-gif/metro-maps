import os
import pandas as pd
import numpy as np
import datetime


def get_edge_labels():

    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.join(root_dir, 'gtfs', 'rab'))

    times = {'7301': pd.read_csv("7301_1.csv", dtype=str, sep=";", header=None),
             '7303': pd.read_csv("7303_1.csv", dtype=str, sep=";", header=None),
             '7304': pd.read_csv("7304_1.csv", dtype=str, sep=";", header=None),
             '7305': pd.read_csv("7305_1.csv", dtype=str, sep=";", header=None),
             '7306': pd.read_csv("7306_1.csv", dtype=str, sep=";", header=None),
             '7307': pd.read_csv("7307_1.csv", dtype=str, sep=";", header=None),
             '7309': pd.read_csv("7309_1.csv", dtype=str, sep=";", header=None),
             '7310': pd.read_csv("7310_1.csv", dtype=str, sep=";", header=None),
             '7311': pd.read_csv("7311_1.csv", dtype=str, sep=";", header=None),
             '7314': pd.read_csv("7314.csv", dtype=str, sep=";", header=None),
             '7315': pd.read_csv("7315.csv", dtype=str, sep=";", header=None),
             '7320': pd.read_csv("7320_1.csv", dtype=str, sep=";", header=None),
             '7321': pd.read_csv("7321_1.csv", dtype=str, sep=";", header=None)}

    modes = {}

    for k in times.keys():
        indices_to_del = []
        for i in range(15, len(times[k])):
            for j in range(2, len(times[k].columns)):
                if times[k][j][i] in ['', '-'] or times[k][j][i] == times[k][j-1][i]:
                    indices_to_del.append((i, j))

        for (i, j) in indices_to_del:
            times[k][j][i] = np.nan

        dep_times = {times[k][0][i]: [] for i in range(15, len(times[k]))}
        for i in range(15, len(times[k])):
            for j in range(2, len(times[k].columns)):
                if not pd.isna(times[k].iloc[i, j]) and times[k][j][i] != '-':
                    dep_time = datetime.datetime.strptime(times[k][j][i], '%H:%M')
                    dep_times[times[k][0][i]] = dep_times[times[k][0][i]] + [dep_time]

        dep_time_diffs = []
        for i in range(15, len(times[k])):
            for j in range(1, len(dep_times[times[k][0][i]])):
                diff = (dep_times[times[k][0][i]][j] - dep_times[times[k][0][i]][j-1]).total_seconds() // 60
                if diff >= 10:
                    dep_time_diffs.append(diff)

        modes[k] = max(dep_time_diffs, key=dep_time_diffs.count)

    return modes
