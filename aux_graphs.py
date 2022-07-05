import networkx as nx

from edge_labels import get_edge_labels


def create_line_graph(grid_graph):

    line_graph = nx.Graph()

    for (x, y) in grid_graph.edges:
        if grid_graph.edges[x, y]['e_type'] not in ['sink', 'bend'] and grid_graph.edges[x, y]['routes']:
            u = (x[0], x[1])
            v = (y[0], y[1])
            line_graph.add_edge(u, v)
            line_graph.edges[u, v]['weight'] = grid_graph.edges[x, y]['weight']
            line_graph.edges[u, v]['routes'] = [int(rou) for rou in grid_graph.edges[x, y]['routes']]

    return line_graph


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def create_color_graph(grid_graph, scale):

    color_graph = nx.Graph()
    color_map = {1: (195, 0, 47), 3: (241, 203, 12), 4: (36, 149, 76), 5: (218, 146, 186), 6: (196, 0, 121),
                 7: (119, 109, 172), 9: (23, 157, 163), 10: (0, 132, 201), 11: (214, 123, 24), 14: (180, 118, 132),
                 15: (216, 195, 123)}

    k = 0

    edge_widths = get_edge_labels()

    for (x, y) in grid_graph.edges:
        if grid_graph.edges[x, y]['e_type'] not in ['sink', 'bend']:
            u = (x[0], x[1])
            v = (y[0], y[1])
            colors = []
            j = 0
            grid_graph.edges[x, y]['routes'] = set(grid_graph.edges[x, y]['routes'])
            for route in grid_graph.edges[x, y]['routes']:
                route_number = int(route)
                rgb_color = tuple(color_map[route_number])
                color = rgb_to_hex(rgb_color)

                if color not in colors:
                    colors.append(color)
                    x_offset = 0
                    y_offset = 0
                    if grid_graph.edges[x, y]['e_type'] == 'h':
                        y_offset = (-1) ** j * (j + 1) / 2 * scale / 25.0
                    else:
                        x_offset = (-1) ** j * (j + 1) / 2 * scale / 25.0

                    if edge_widths['73' + route] <= 15:
                        edge_style = ''
                    elif edge_widths['73' + route] <= 30:
                        edge_style = 'dash'
                    elif edge_widths['73' + route] <= 60:
                        edge_style = 'dot'
                    else:
                        edge_style = 'dashdot'

                    color_graph.add_node(2 * k, pos=(grid_graph.nodes[u]['pos'][0] + x_offset,
                                                     grid_graph.nodes[u]['pos'][1] + y_offset),
                                         gri_node=grid_graph.nodes[u]['ident'])
                    color_graph.add_node(2 * k + 1, pos=(grid_graph.nodes[v]['pos'][0] + x_offset,
                                                         grid_graph.nodes[v]['pos'][1] + y_offset),
                                         gri_node=grid_graph.nodes[v]['ident'])

                    color_graph.add_edge(2 * k, 2 * k + 1, e_color=color, e_style=edge_style)
                    color_graph.nodes[2 * k]['n_size'] = 0
                    color_graph.nodes[2 * k + 1]['n_size'] = 0

                    if j == 0:
                        if grid_graph.nodes[u]['drawn']:
                            color_graph.nodes[2 * k]['n_size'] = scale / 1000.0
                        if grid_graph.nodes[v]['drawn']:
                            color_graph.nodes[2 * k + 1]['n_size'] = scale / 1000.0

                    j += 1
                    k += 1

    return color_graph
