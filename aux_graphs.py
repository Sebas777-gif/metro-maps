import networkx as nx

from edge_labels import get_edge_labels


def create_line_graph(grid_graph):

    line_graph = nx.Graph()

    for x in grid_graph.nodes:
        line_graph.add_node((x[0], x[1]))
        line_graph.nodes[(x[0], x[1])]['orig_node'] = x

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


def create_colors(route_lines):

    colors = {}
    color_map = {1: (195, 0, 47), 3: (241, 203, 12), 4: (36, 149, 76), 5: (218, 146, 186), 6: (196, 0, 121),
                 7: (119, 109, 172), 9: (23, 157, 163), 10: (0, 132, 201), 11: (214, 123, 24), 14: (180, 118, 132),
                 15: (216, 195, 123)}

    edge_widths = get_edge_labels()
    for route in route_lines.keys():
        route_number = int(route)
        rgb_color = tuple(color_map[route_number])
        color = rgb_to_hex(rgb_color)

        if edge_widths['73' + route] <= 15:
            edge_style = ''
        elif edge_widths['73' + route] <= 30:
            edge_style = 'dash'
        elif edge_widths['73' + route] <= 60:
            edge_style = 'dot'
        else:
            edge_style = 'dashdot'

        colors[route] = (color, edge_style)

    return colors
