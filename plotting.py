import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse
import os
import math
import json
import sys

from redirect import Redirect


LINE_WIDTH = 0.1

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(ROOT_DIR, 'gtfs'))

directions = {0: 'block_n', 1: 'block_ne', 2: 'block_e', 3: 'block_se',
              4: 'block_s', 5: 'block_sw', 6: 'block_w', 7: 'block_nw'}
neighbors = {0: 'neighbor_n', 1: 'neighbor_ne', 2: 'neighbor_e', 3: 'neighbor_se',
             4: 'neighbor_s', 5: 'neighbor_sw', 6: 'neighbor_w', 7: 'neighbor_nw'}
geometry = {0: (0, -1), 1: (-1, -1), 2: (-1, 0), 3: (-1, 1), 4: (0, 1), 5: (1, 1), 6: (1, 0), 7: (1, -1)}


def do_polygons_intersect(a, b):

    for poly in [a, b]:

        for i1 in range(len(poly)):
            i2 = (i1 + 1) % len(poly)
            p1 = poly[i1]
            p2 = poly[i2]

            normal = (p2[1] - p1[1], p1[0] - p2[0])

            min_a = float('inf')
            max_a = - float('inf')
            for p in a:
                projected = normal[0] * p[0] + normal[1] * p[1]
                min_a = min(min_a, projected)
                max_a = max(max_a, projected)

            min_b = float('inf')
            max_b = - float('inf')
            for p in b:
                projected = normal[0] * p[0] + normal[1] * p[1]
                min_b = min(min_b, projected)
                max_b = max(max_b, projected)

            if max_a < min_b or max_b < min_a:
                return False

    return True



def make_length(v, length):
    current_len = math.sqrt(v[0] ** 2 + v[1] ** 2)
    return v[0] / current_len * length, v[1] / current_len * length


def pos_prio(x):
    if x in [2, 6]:
        return 0
    elif x in [1, 3, 5, 7]:
        return 1
    elif x in [0, 4]:
        return 2
    else:
        raise ValueError('Argument must be integer between 0 and 7.')


def check_for_collisions(grid_graph, node, pos, label_len, label_hgt):

    if geometry[pos][0] >= 0:
        x_corr = 0.01
    else:
        x_corr = -0.01
    if geometry[pos][1] >= 0:
        y_corr = 0.01
    else:
        y_corr = -0.01

    node_1 = (node[0] + x_corr, node[1] + y_corr)
    node_2 = (node_1[0] + make_length(geometry[pos], label_len)[0],
              node_1[1] + make_length(geometry[pos], label_len)[1])
    node_3 = (node_2[0] + make_length(geometry[(pos + 2) % 8], label_hgt)[0],
              node_2[1] + make_length(geometry[(pos + 2) % 8], label_hgt)[1])
    node_4 = (node_3[0] + make_length(geometry[(pos + 4) % 8], label_len)[0],
              node_3[1] + make_length(geometry[(pos + 4) % 8], label_len)[1])
    node_poly = [node_1, node_2, node_3, node_4]

    for nb_node in nx.ego_graph(grid_graph, node, radius=2 * label_len, distance='alt_weight').nodes:

        nb_node = (nb_node[0], nb_node[1])

        if not grid_graph.nodes[nb_node]['drawn'] or nb_node == node:
            continue

        if grid_graph.nodes[nb_node]['label_dir'] != -1:
            nb_label_len = grid_graph.nodes[nb_node]['label_len']
            nb_label_hgt = grid_graph.nodes[nb_node]['label_hgt']
            direction = grid_graph.nodes[nb_node]['label_dir']
            if geometry[direction][0] >= 0:
                x_corr = 0.03
            else:
                x_corr = -0.03
            if geometry[direction][1] >= 0:
                y_corr = 0.03
            else:
                y_corr = -0.03
            nb_node_1 = (nb_node[0] + x_corr, nb_node[1] + y_corr)
            nb_node_2 = (nb_node_1[0] + make_length(geometry[direction], nb_label_len)[0],
                         nb_node_1[1] + make_length(geometry[direction], nb_label_len)[1])
            nb_node_3 = (nb_node_2[0] + make_length(geometry[(direction + 2) % 8], nb_label_hgt)[0],
                         nb_node_2[1] + make_length(geometry[(direction + 2) % 8], nb_label_hgt)[1])
            nb_node_4 = (nb_node_3[0] + make_length(geometry[(direction + 4) % 8], nb_label_len)[0],
                         nb_node_3[1] + make_length(geometry[(direction + 4) % 8], nb_label_len)[1])
            nb_poly = [nb_node_1, nb_node_2, nb_node_3, nb_node_4]
        else:
            continue

        if do_polygons_intersect(node_poly, nb_poly):
            return True

    for nb_edge in nx.ego_graph(grid_graph, node, radius=3 * label_len, distance='alt_weight').edges:

        if grid_graph.edges[nb_edge]['e_type'] not in ['h', 'v', 'd1', 'd2'] \
                or not grid_graph.edges[nb_edge]['routes'] or nb_edge[0][:2] == node or nb_edge[1][:2] == node:
            continue

        p_1 = nb_edge[0]
        p_2 = nb_edge[1]
        edge_vec = (p_2[1] - p_1[1], p_1[0] - p_2[0])  # rotated by 90 degrees counter-clockwise

        no_routes = len(grid_graph.edges[nb_edge]['routes'])
        nb_node_1 = (p_1[0], p_1[1])
        nb_node_2 = (p_1[0] + make_length(edge_vec, no_routes * LINE_WIDTH)[0],
                     p_1[1] + make_length(edge_vec, no_routes * LINE_WIDTH)[1])
        nb_node_3 = (p_2[0], p_2[1])
        nb_node_4 = (p_2[0] + make_length(edge_vec, no_routes * LINE_WIDTH)[0],
                     p_2[1] + make_length(edge_vec, no_routes * LINE_WIDTH)[1])
        nb_poly = [nb_node_1, nb_node_2, nb_node_3, nb_node_4]

        if do_polygons_intersect(node_poly, nb_poly):
            return True

    return False

def place_label(grid_graph, node, stop_label):

    possible_pos = [i for i in range(8) if grid_graph.nodes[node][directions[i]] == 0]
    possible_pos.sort(key=pos_prio)
    # MAGIC
    label_len = max([len(label) for label in stop_label.split('\n')]) * 0.15
    label_hgt = len(stop_label.split('\n')) * 0.15

    i = -1
    collision = True
    pos = possible_pos[0]

    while collision and i < len(possible_pos) - 1:
        i += 1
        pos = possible_pos[i]
        collision = check_for_collisions(grid_graph, node, pos, label_len, label_hgt)

    if collision:
        pos = possible_pos[0]

    grid_graph.nodes[node]['label_len'] = label_len
    grid_graph.nodes[node]['label_hgt'] = label_hgt
    grid_graph.nodes[node]['label_dir'] = pos


def convert_string(s):
    numbers = s.split(',')
    return float(numbers[0]), float(numbers[1])


def get_dir(a, b):
    if a[0] < b[0]:
        if a[1] < b[1]:
            return 5
        elif a[1] > b[1]:
            return 7
        else:
            return 6
    elif a[0] > b[0]:
        if a[1] < b[1]:
            return 3
        elif a[1] > b[1]:
            return 1
        else:
            return 2
    else:
        if a[1] < b[1]:
            return 4
        else:
            return 0


def find_lines(route_lists):

    straight_lines = {rou_id: [] for rou_id in route_lists.keys()}
    for rou_id in route_lists.keys():
        rou = route_lists[rou_id]
        old_dir = -1
        lines = [[]]
        for stop_1, stop_2 in zip(rou, rou[1:]):
            new_dir = get_dir(convert_string(stop_1), convert_string(stop_2))
            if old_dir == new_dir or old_dir == -1:
                lines[-1].append(convert_string(stop_2))
            else:
                lines.append([convert_string(stop_1), convert_string(stop_2)])
            old_dir = new_dir
        straight_lines[rou_id] = lines
    return straight_lines


def optimize(grid_graph, line):
    invert_trans_table = [2, 6, 1, 3, 5, 7, 0, 4]
    fitting_labels     = [0, 0, 0, 0, 0, 0, 0, 0]
    trans_table        = [6, 2, 0, 3, 7, 4, 1, 5]
    for x in line:
        label_len = grid_graph.nodes[x]['label_len']
        label_hgt = grid_graph.nodes[x]['label_hgt']
        for i in range(8):
            if grid_graph.nodes[x][directions[i]] == 0 and not check_for_collisions(grid_graph, x, i, label_len,
                                                                                    label_hgt):
                fitting_labels[trans_table[i]] =  fitting_labels[trans_table[i]] + 1
    return invert_trans_table[np.argmax(fitting_labels)]


def optimize_consistency(grid_graph, straight_lines):
    settled = {x: False for x in grid_graph.nodes}
    i = 0
    for rou_lines in straight_lines.values():
        rou_lines.sort(key=len, reverse=True)
        i += 1
        for line in rou_lines:
            pos = optimize(grid_graph, line)
            for x in line:
                if not check_for_collisions(grid_graph, x, pos, grid_graph.nodes[x]['label_len'],
                                            grid_graph.nodes[x]['label_hgt'])\
                        and grid_graph.nodes[x][directions[pos]] == 0 and not settled[x]\
                        and grid_graph.nodes[x][directions[pos]] == 0:
                    grid_graph.nodes[x]['label_dir'] = pos
                    settled[x] = True
        print("Linie {} von {} optimiert.".format(i, len(straight_lines)))


def plot_graph(grids, scale, search_radius, bend_factor, geo_penalty, text):

    sys.stdout = Redirect(text)

    col_graph = nx.read_gpickle('color_graph_' + str(search_radius) + '.pickle')
    grid_graph = nx.read_gpickle('grid_graph_' + str(search_radius) + '.pickle')

    edges_full = [e for e in col_graph.edges if col_graph.edges[e]['e_style'] == '']
    colors_full = [col_graph.edges[e]['e_color'] for e in col_graph.edges if col_graph.edges[e]['e_style'] == '']
    colors_dash = [col_graph.edges[e]['e_color'] for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dash']
    colors_dot = [col_graph.edges[e]['e_color'] for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dot']
    colors_dashdot = [col_graph.edges[e]['e_color'] for e in col_graph.edges
                      if col_graph.edges[e]['e_style'] == 'dashdot']
    edges_dash = [e for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dash']
    edges_dot = [e for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dot']
    edges_dashdot = [e for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dashdot']
    fig = plt.figure(1)
    ax = fig.add_subplot(1, 1, 1, aspect='equal')

    nx.draw_networkx_nodes(col_graph, nx.get_node_attributes(col_graph, 'pos'), node_size=0, ax=ax)
    nx.draw_networkx_edges(col_graph, nx.get_node_attributes(col_graph, 'pos'), edgelist=edges_full, ax=ax,
                           width=scale / 500.0, edge_color=colors_full, connectionstyle='arc3, rad = 0')
    nx.draw_networkx_edges(col_graph, nx.get_node_attributes(col_graph, 'pos'), edgelist=edges_dash, ax=ax,
                           width=scale / 500.0, edge_color=colors_dash, connectionstyle='arc3, rad = 0', style='dashed')
    nx.draw_networkx_edges(col_graph, nx.get_node_attributes(col_graph, 'pos'), edgelist=edges_dot, ax=ax,
                           width=scale / 500.0, edge_color=colors_dot, connectionstyle='arc3, rad = 0', style='dotted')
    nx.draw_networkx_edges(col_graph, nx.get_node_attributes(col_graph, 'pos'), edgelist=edges_dashdot, ax=ax,
                           width=scale / 500.0, edge_color=colors_dashdot,
                           connectionstyle='arc3, rad = 0', style='dashdot')

    node_list = sorted([node for node in grid_graph.nodes if grid_graph.nodes[node]['geo_dist'] >= 0
                        and grid_graph.nodes[node]['drawn']], key=lambda x: grid_graph.nodes[x]['geo_dist'])
    beaut_labels = {}
    i = 0
    for node in node_list:
        i += 1
        # make the labels a bit more beautiful
        st_label = grid_graph.nodes[node]['stop_label']
        if st_label.startswith('Ravensburg') or st_label.startswith('Weingarten'):
            st_label = st_label[11:]
        elif st_label.startswith('RV,'):
            st_label = st_label[4:]
        elif st_label.startswith('RV'):
            st_label = st_label[3:]
        words = st_label.split()
        final_label = words[0]
        j = 0
        while j < len(words) - 1:
            j += 1
            if len(final_label + words[j]) < len(st_label) / 2:
                final_label += ' ' + words[j]
            else:
                final_label += '\n' + words[j]
                break
        while j < len(words) - 1:
            j += 1
            final_label += ' ' + words[j]

        place_label(grid_graph, node, final_label)
        beaut_labels[node] = final_label
        print("Label {} von {} platziert.".format(i, len(node_list)))

    with open('route_lists_s' + str(search_radius) + 'gr' + str(grids) + 'b' + str(bend_factor) + 'geo' +
              str(geo_penalty) + '.json') as json_file:
        route_lists = json.load(json_file)
    straight_lines = find_lines(route_lists)
    optimize_consistency(grid_graph, straight_lines)

    for w, (x, y) in nx.get_node_attributes(grid_graph, 'pos').items():

        if w not in node_list:
            continue

        turn = grid_graph.nodes[w]['label_dir']

        angle = (2 - turn) * 45

        if turn in [2, 3]:
            x_fac = 1
        elif turn in [5, 6, 7]:
            x_fac = -1
        elif turn == 1:
            x_fac = 1.5
        else:
            x_fac = 0

        if turn in [2, 3, 5, 6]:
            y_fac = -1
        elif turn in [0, 1, 7]:
            y_fac = 1
        else:
            y_fac = 0

        upd = turn in [5, 6, 7]

        if upd:
            ax.text(x + x_fac * scale / 10.0, y + y_fac * scale / 10.0, beaut_labels[w],
                    horizontalalignment='right', fontsize=scale / 400.0, rotation=angle - 180, rotation_mode='anchor')
        else:
            ax.text(x + x_fac * scale / 10.0, y + y_fac * scale / 10.0, beaut_labels[w],
                    fontsize=scale / 400.0, rotation=angle, rotation_mode='anchor')

    drawn_nodes = []
    for node in col_graph.nodes:
        if col_graph.nodes[node]['n_size'] > 0:
            pos = col_graph.nodes[node]['pos']
            actual_node = col_graph.nodes[node]['gri_node']
            if actual_node not in drawn_nodes:
                drawn_nodes.append(actual_node)
                gri_node = [x for x, ide in nx.get_node_attributes(grid_graph, 'ident').items() if ide
                            == col_graph.nodes[node]['gri_node']][0]
                hgt = max(grid_graph.nodes[gri_node]['block_ne'], grid_graph.nodes[gri_node]['block_n'],
                          grid_graph.nodes[gri_node]['block_nw'], grid_graph.nodes[gri_node]['block_s'],
                          grid_graph.nodes[gri_node]['block_se'], grid_graph.nodes[gri_node]['block_sw'],
                          grid_graph.nodes[gri_node]['block_e'], grid_graph.nodes[gri_node]['block_w'])
                hgt = math.log2(hgt + 2)

                circle = Ellipse(pos, height=hgt * scale / 10.0, width=hgt * scale / 10.0, linewidth=scale / 1000.0,
                                 facecolor='white', edgecolor='black', fill=True)
                ax.add_patch(circle)

    plt.savefig('fahrplan_s' + str(search_radius) + 'gr' + str(grids) + 'b' + str(bend_factor) + 'geo'
                + str(geo_penalty) + '.pdf', dpi=1400)
    print("Abgeschlossen.")


def plot_grid(grids, scale, search_radius, bend_factor, geo_penalty):
    col_graph = nx.read_gpickle('color_graph_' + str(search_radius) + '.pickle')
    grid_graph = nx.read_gpickle('grid_graph_' + str(search_radius) + '.pickle')
    edges_full = [e for e in col_graph.edges if col_graph.edges[e]['e_style'] == '']
    colors_full = [col_graph.edges[e]['e_color'] for e in col_graph.edges if col_graph.edges[e]['e_style'] == '']
    colors_dash = [col_graph.edges[e]['e_color'] for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dash']
    colors_dot = [col_graph.edges[e]['e_color'] for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dot']
    colors_dashdot = [col_graph.edges[e]['e_color'] for e in col_graph.edges
                      if col_graph.edges[e]['e_style'] == 'dashdot']
    edges_dash = [e for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dash']
    edges_dot = [e for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dot']
    edges_dashdot = [e for e in col_graph.edges if col_graph.edges[e]['e_style'] == 'dashdot']
    fig = plt.figure(1)
    ax = fig.add_subplot(1, 1, 1, aspect='equal')

    grid_edges = [e for e in grid_graph.edges if grid_graph.edges[e]['e_type'] in ['h', 'v', 'd1', 'd2']]
    nx.draw_networkx_edges(grid_graph, nx.get_node_attributes(grid_graph, 'pos'), edgelist=grid_edges,
                           edge_color='grey',
                           width=scale / 1000.0)

    nx.draw_networkx_nodes(col_graph, nx.get_node_attributes(col_graph, 'pos'), node_size=0)
    nx.draw_networkx_edges(col_graph, nx.get_node_attributes(col_graph, 'pos'), edgelist=edges_full,
                           width=scale / 500.0, edge_color=colors_full, connectionstyle='arc3, rad = 0')
    nx.draw_networkx_edges(col_graph, nx.get_node_attributes(col_graph, 'pos'), edgelist=edges_dash,
                           width=scale / 500.0, edge_color=colors_dash, connectionstyle='arc3, rad = 0', style='dashed')
    nx.draw_networkx_edges(col_graph, nx.get_node_attributes(col_graph, 'pos'), edgelist=edges_dot,
                           width=scale / 500.0, edge_color=colors_dot, connectionstyle='arc3, rad = 0', style='dotted')
    nx.draw_networkx_edges(col_graph, nx.get_node_attributes(col_graph, 'pos'), edgelist=edges_dashdot,
                           width=scale / 500.0, edge_color=colors_dashdot,
                           connectionstyle='arc3, rad = 0', style='dashdot')

    drawn_nodes = []
    for node in col_graph.nodes:
        if col_graph.nodes[node]['n_size'] > 0:
            pos = col_graph.nodes[node]['pos']
            actual_node = col_graph.nodes[node]['gri_node']
            if actual_node not in drawn_nodes:
                drawn_nodes.append(actual_node)
                gri_node = [x for x, ide in nx.get_node_attributes(grid_graph, 'ident').items() if ide
                            == col_graph.nodes[node]['gri_node']][0]
                hgt = max(grid_graph.nodes[gri_node]['block_ne'], grid_graph.nodes[gri_node]['block_n'],
                          grid_graph.nodes[gri_node]['block_nw'], grid_graph.nodes[gri_node]['block_s'],
                          grid_graph.nodes[gri_node]['block_se'], grid_graph.nodes[gri_node]['block_sw'],
                          grid_graph.nodes[gri_node]['block_e'], grid_graph.nodes[gri_node]['block_w'])
                hgt = math.log2(hgt + 2)

                circle = Ellipse(pos, height=hgt * scale / 10.0, width=hgt * scale / 10.0, linewidth=scale / 1000.0,
                                 facecolor='white', edgecolor='black', fill=True)
                ax.add_patch(circle)

    plt.savefig('fahrplan_s' + str(search_radius) + 'gr' + str(grids) + 'b' + str(bend_factor) + 'geo'
                + str(geo_penalty) + '_grid.pdf', dpi=1000)
