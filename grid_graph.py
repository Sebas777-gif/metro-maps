import math
import networkx as nx
import bisect


def setup_grid_graph(stations, lines, stop_labels, scale, lon_size, lat_size, bend_factor):
    """

    :param stations:
    :param lines:
    :param stop_labels:
    :param scale:
    :param lon_size:
    :param lat_size:
    :param bend_factor:
    :return:
    """
    grid_graph = nx.Graph()

    points = {line: [] for line in lines}
    coord_list = []
    for line_1 in lines:
        for line_2 in lines:
            intersection = line_intersection(line_1, line_2)
            if intersection != (-1, -1) and intersection not in points[line_1]:
                bisect.insort(points[line_1], intersection)
                coord_list.append(intersection)

    coord_list.sort()

    for i in range(len(coord_list)):
        grid_graph.add_node(coord_list[i], ident=coord_list[i], ids=[], pos=((lon_size - coord_list[i][0]) * scale,
                                                                             (lat_size - coord_list[i][1]) * scale),
                            block_n=0, block_w=0, block_s=0, block_e=0,
                            block_nw=0, block_sw=0, block_se=0, block_ne=0,
                            neighbor_n=-1, neighbor_w=-1, neighbor_s=-1, neighbor_e=-1,
                            neighbor_nw=-1, neighbor_sw=-1, neighbor_se=-1, neighbor_ne=-1, label_dir=-1,
                            stop_label='', node_type='standard', drawn=False, geo_dist=-1, label_len=0, label_hgt=0)
        for j in range(8):
            grid_graph.add_node((coord_list[i][0], coord_list[i][1], j), node_type='port', geo_dist=-1, label_length=0,
                                pos=((lon_size - coord_list[i][0]) * scale, (lat_size - coord_list[i][1]) * scale),
                                label_dir=-1)
            grid_graph.add_edge(coord_list[i], (coord_list[i][0], coord_list[i][1], j), weight=3*bend_factor,
                                alt_weight=0, e_type='sink')

        for j in range(8):
            for k in range(1, 8 - j):
                cost = bend_factor * abs(k - 4)
                grid_graph.add_edge((coord_list[i][0], coord_list[i][1], j),
                                    (coord_list[i][0], coord_list[i][1], j + k),
                                    weight=cost, alt_weight=0, e_type='bend')
        if coord_list[i] in stations:
            grid_graph.nodes[coord_list[i]]['stop_label'] = stop_labels[coord_list[i]].get_stop_name()

    for line in lines:
        # horizontal edges
        if line[0][1] == line[1][1]:
            for (p_1, p_2) in zip(points[line], points[line][1:]):
                grid_graph.add_edge((p_1[0], p_1[1], 2), (p_2[0], p_2[1], 6), weight=p_2[0] - p_1[0], routes=[],
                                    alt_weight=p_2[0] - p_1[0], e_type='h')

                grid_graph.nodes[p_1]['neighbor_e'] = p_2
                grid_graph.nodes[p_2]['neighbor_w'] = p_1
        # vertical edges
        elif line[0][0] == line[1][0]:
            for (p_1, p_2) in zip(points[line], points[line][1:]):
                grid_graph.add_edge((p_1[0], p_1[1], 4), (p_2[0], p_2[1], 0), weight=p_2[1] - p_1[1], routes=[],
                                    alt_weight=p_2[1] - p_1[1], e_type='v')

                grid_graph.nodes[p_1]['neighbor_s'] = p_2
                grid_graph.nodes[p_2]['neighbor_n'] = p_1
        # diagonal from lower left to upper right
        elif line[1][1] - line[0][1] == -1:
            for (p_1, p_2) in zip(points[line], points[line][1:]):
                length = math.sqrt((p_2[0] - p_1[0]) ** 2 + (p_2[1] - p_1[1]) ** 2)
                grid_graph.add_edge((p_1[0], p_1[1], 1), (p_2[0], p_2[1], 5), weight=length, routes=[],
                                    alt_weight=length, e_type='d2')

                grid_graph.nodes[p_1]['neighbor_ne'] = p_2
                grid_graph.nodes[p_2]['neighbor_sw'] = p_1
        # diagonal from upper left to lower right
        else:
            for (p_1, p_2) in zip(points[line], points[line][1:]):
                length = math.sqrt((p_2[0] - p_1[0]) ** 2 + (p_2[1] - p_1[1]) ** 2)
                grid_graph.add_edge((p_1[0], p_1[1], 3), (p_2[0], p_2[1], 7), weight=length, routes=[],
                                    alt_weight=length, e_type='d1')

                grid_graph.nodes[p_1]['neighbor_se'] = p_2
                grid_graph.nodes[p_2]['neighbor_nw'] = p_1

    return grid_graph


def line_intersection(line1, line2):
    x_diff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    y_diff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(x_diff, y_diff)
    if div == 0:
        return -1, -1

    d = (det(*line1), det(*line2))
    x = det(d, x_diff) / div
    y = det(d, y_diff) / div
    return x, y
