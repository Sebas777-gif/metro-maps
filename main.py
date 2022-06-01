import copy
import pandas as pd
import networkx as nx
import math
import os
import sys
import json

from collections import OrderedDict
from aux_graphs import create_line_graph, create_color_graph
from grid_graph import setup_grid_graph
from stops_class import Stop


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(ROOT_DIR, 'gtfs'))
routes = pd.read_csv("routes.txt")
agency_routes = routes[routes['route_id'].str.contains('7-3(0(1|3|[4-7]|9)|1(0|1|4|5)|2(0|1))')]  # Stadtbus RV-Wgt
agency_route_ids = agency_routes.route_id.tolist()

trips = pd.read_csv("trips.txt")
agency_trips_1 = trips[trips['route_id'].isin(agency_route_ids)]
agency_trips = agency_trips_1[agency_trips_1['service_id'].str.contains('T0')]
agency_trip_ids = agency_trips.trip_id.tolist()

stop_times = pd.read_csv("stop_times.txt")
agency_stop_times = stop_times[stop_times['trip_id'].isin(agency_trip_ids)]
agency_stop_ids = agency_stop_times.stop_id.tolist()

stops = pd.read_csv("stops.txt")
agency_stops = stops[stops['stop_id'].isin(agency_stop_ids)]


def save_graphs(gri_graph, col_graph, radius):
    nx.write_gpickle(gri_graph, 'grid_graph_' + str(radius) + '.pickle')
    nx.write_gpickle(col_graph, 'color_graph_' + str(radius) + '.pickle')


def get_lon_size():
    l_max = agency_stops.stop_lon.max()
    l_min = agency_stops.stop_lon.min()
    return l_max - l_min


def get_lat_size():
    l_max = agency_stops.stop_lat.max()
    l_min = agency_stops.stop_lat.min()
    return l_max - l_min


def main(grids, scale, search_radius, bend_factor, geo_penalty):


    orig_grids = grids
    THRESHOLD = 3 * search_radius

    lon_size = get_lon_size()
    lon_step = lon_size / (grids - 1)
    lon_min = agency_stops.stop_lon.min()

    lat_size = get_lat_size()
    lat_step = lat_size / (grids - 1)
    lat_min = agency_stops.stop_lat.min()

    lines = []
    stations = []
    stops = {}
    stop_labels = {}
    ids_of_names = {agency_stops['stop_name'][ind]: [] for ind in agency_stops.index}
    ids_of_coods = {}
    stop_coods_of_names = {}
    stop_coods = {}
    labels_of_ids = {}
    orig_coods = {}

    min_frac = 1

    for ind in agency_stops.index:
        ids_of_names[agency_stops['stop_name'][ind]] \
            = ids_of_names[agency_stops['stop_name'][ind]] + [agency_stops['stop_id'][ind]]

    for ind in agency_stops.index:
        lon = int((agency_stops['stop_lon'][ind] - lon_min) / lon_step + 0.5)
        lat = int((agency_stops['stop_lat'][ind] - lat_min) / lat_step + 0.5)
        if agency_stops['stop_name'][ind] not in stop_labels.values():

            if (lon, lat) in ids_of_coods:
                if orig_coods[(lon, lat)][0] > agency_stops['stop_lon'][ind]:
                    new_lon = lon - (int(lon) - lon + 1) / 2
                else:
                    new_lon = lon + (int(lon) - lon + 1) / 2
                if orig_coods[(lon, lat)][1] > agency_stops['stop_lat'][ind]:
                    new_lat = lat - (int(lat) - lat + 1) / 2
                else:
                    new_lat = lat + (int(lat) - lat + 1) / 2
                grids += 1
                new_coods = [(lon, new_lat), (new_lon, lat), (new_lon, new_lat)]
                min_frac = min(min_frac, int(lon) - lon + 1, int(lat) - lat + 1)
            else:
                new_coods = [(lon, lat)]

            orig_coods[(lon, lat)] = (agency_stops['stop_lon'][ind], agency_stops['stop_lat'][ind])

            for (x, y) in new_coods:
                line_1 = ((x, y), (x + 1, y))
                line_2 = ((x, y), (x, y + 1))
                line_3 = ((x, y), (x + 1, y + 1))
                line_4 = ((x, y), (x + 1, y - 1))
                lines += [line_1, line_2, line_3, line_4]
            stations.append(new_coods[-1])
            stops[new_coods[-1]] = Stop(new_coods[-1][0], new_coods[-1][1], agency_stops['stop_name'][ind],
                                        agency_stops['stop_id'][ind])
            stop_labels[new_coods[-1]] = agency_stops['stop_name'][ind]
            ids_of_coods[new_coods[-1]] = [agency_stops['stop_id'][ind]]
            stop_coods_of_names[agency_stops['stop_name'][ind]] = new_coods[-1]
            stop_coods[agency_stops['stop_id'][ind]] = new_coods[-1]

        else:
            coods = stop_coods_of_names[agency_stops['stop_name'][ind]]
            ids_of_coods[coods] += [agency_stops['stop_id'][ind]]
            stop_coods[agency_stops['stop_id'][ind]] = coods

        labels_of_ids[agency_stops['stop_id'][ind]] = agency_stops['stop_name'][ind]

    grid_graph = setup_grid_graph(stations, lines, stops, scale, lon_size, lat_size, bend_factor)
    min_frac = max(0.25, min_frac)

    stops_set = list(set(stops.values()))

    routes_of_pairs = {(stop_1.get_stop_name(), stop_2.get_stop_name()): [] for stop_1 in stops_set for stop_2 in
                       stops_set}
    route_lists = {rou_id[3:5]: [] for rou_id in agency_route_ids}
    for rou_id in agency_route_ids:

        trip_ids = agency_trips[agency_trips.route_id == rou_id].trip_id.tolist()
        cons_route = []
        route_trips = []

        for trip_id in trip_ids:
            route_stops = agency_stop_times[agency_stop_times.trip_id == trip_id]
            trip = []
            for stop in route_stops["stop_id"].values:
                trip.append(stops[stop_coods[stop]])
            route_trips.append(trip)

        route_trips.sort(key=len, reverse=True)
        if route_trips:
            cons_route = route_trips[0]

        if len(cons_route) > len(route_lists[rou_id[3:5]]):
            route_lists[rou_id[3:5]] = cons_route

    route_lists = OrderedDict(sorted(route_lists.items(), key=lambda li: len(li[1]), reverse=True))


    for route in route_lists.keys():
        for stop_1, stop_2 in zip(route_lists[route], route_lists[route][1:]):
            routes_of_pairs[(labels_of_ids[stop_1.get_id()], labels_of_ids[stop_2.get_id()])].append(route)

    point_routes = {x: [] for x in grid_graph.nodes if grid_graph.nodes[x]['node_type'] == 'standard'}

    grid_graph, stop_coods = calculate_paths(grid_graph, route_lists, stops, stop_coods, point_routes, search_radius,
                                             bend_factor, geo_penalty, min_frac, THRESHOLD)

    route_lists_strings = {rou_id[3:5]: [] for rou_id in agency_route_ids}
    for rou_id in agency_route_ids:

        trip_ids = agency_trips[agency_trips.route_id == rou_id].trip_id.tolist()
        cons_route_string = []
        route_trips_strings = []

        for trip_id in trip_ids:
            route_stops = agency_stop_times[agency_stop_times.trip_id == trip_id]
            trip_strings = []
            for stop in route_stops["stop_id"].values:
                trip_strings.append(str(stop_coods[stop][0]) + ',' + str(stop_coods[stop][1]))
            route_trips_strings.append(trip_strings)

        route_trips_strings.sort(key=len, reverse=True)
        if route_trips_strings:
            cons_route_string = route_trips_strings[0]

        if len(cons_route_string) > len(route_lists_strings[rou_id[3:5]]):
            route_lists_strings[rou_id[3:5]] = cons_route_string

    route_lists_strings = OrderedDict(sorted(route_lists_strings.items(), key=lambda li: len(li[1]), reverse=True))

    with open('route_lists_s' + str(search_radius) + 'gr' + str(orig_grids) + 'b' + str(bend_factor) + 'geo' +
              str(geo_penalty) + '.json', 'w') as outfile:
        json.dump(route_lists_strings, outfile)

    for (u, v) in grid_graph.edges:
        x = (u[0], u[1])
        y = (v[0], v[1])
        if grid_graph.edges[u, v]['e_type'] == 'h' and grid_graph.edges[u, v]['routes']:
            if x[0] < y[0]:
                x, y = y, x
            grid_graph.nodes[x]['block_e'] += len(set(grid_graph.edges[u, v]['routes']))
            grid_graph.nodes[y]['block_w'] += len(set(grid_graph.edges[u, v]['routes']))
        elif grid_graph.edges[u, v]['e_type'] == 'v' and grid_graph.edges[u, v]['routes']:
            if x[1] > y[1]:
                x, y = y, x
            grid_graph.nodes[x]['block_s'] += len(set(grid_graph.edges[u, v]['routes']))
            grid_graph.nodes[y]['block_n'] += len(set(grid_graph.edges[u, v]['routes']))
        elif grid_graph.edges[u, v]['e_type'] == 'd1' and grid_graph.edges[u, v]['routes']:
            if x[0] < y[0]:
                x, y = y, x
            grid_graph.nodes[x]['block_ne'] += len(set(grid_graph.edges[u, v]['routes']))
            grid_graph.nodes[y]['block_sw'] += len(set(grid_graph.edges[u, v]['routes']))
        elif grid_graph.edges[u, v]['e_type'] == 'd2' and grid_graph.edges[u, v]['routes']:
            if x[0] < y[0]:
                x, y = y, x
            grid_graph.nodes[x]['block_se'] += len(set(grid_graph.edges[u, v]['routes']))
            grid_graph.nodes[y]['block_nw'] += len(set(grid_graph.edges[u, v]['routes']))

    color_graph = create_color_graph(grid_graph, scale)
    skel_graph = create_line_graph(grid_graph)

    geo_dists = geodesic_dists(grid_graph, stops, skel_graph)
    for st in [st for st in stops.keys() if grid_graph.nodes[st]['drawn']]:
        grid_graph.nodes[st]['geo_dist'] = geo_dists[st]

    save_graphs(grid_graph, color_graph, search_radius)


def calculate_paths(gri_graph, rou_lists, stops, stop_coods, point_routes, search_radius, bend_factor, geo_penalty, min_frac,
                    threshold):

    cnt = 0

    for rou in rou_lists.keys():

        grid_graph_copy = copy.deepcopy(gri_graph)
        for st in stops.values():
            if st.get_stop_name() not in [station.get_stop_name() for station in rou_lists[rou]] \
                    and st.is_settled():
                st_node = st.get_coods()
                for i in range(8):
                    grid_graph_copy.edges[st_node, (st_node[0], st_node[1], i)]['weight'] = 1250 * bend_factor
                    for j in range(1, 8 - i):
                        grid_graph_copy.edges[(st_node[0], st_node[1], i), (st_node[0], st_node[1], i + j)]['weight'] \
                            = 1000 * bend_factor * abs(j - 4)

        for m in range(len(rou_lists[rou]) - 1):

            st = rou_lists[rou][m]
            nb = rou_lists[rou][m + 1]
            st_node = st.get_coods()
            nb_node = nb.get_coods()
            source_candidates = [st_node]
            target_candidates = [nb_node]

            if not st.is_settled() or not nb.is_settled():
                source_candidates, target_candidates = get_candidates(gri_graph, stops, st, nb, st_node, nb_node,
                                                                      min_frac, search_radius, threshold)

            if m == 0 and nb.is_settled():
                for i in range(8):
                    grid_graph_copy.edges[nb_node, (nb_node[0], nb_node[1], i)]['weight'] = 3 * bend_factor
                    for j in range(1, 8 - i):
                        grid_graph_copy.edges[(nb_node[0], nb_node[1], i), (nb_node[0], nb_node[1], i + j)]['weight'] \
                            = bend_factor * abs(j - 4)

            final_src = st_node
            final_tgt = nb_node
            min_sp = nx.bidirectional_dijkstra(grid_graph_copy, source=st_node, target=nb_node, weight="weight")[1]
            min_length = nx.bidirectional_dijkstra(grid_graph_copy, source=st_node, target=nb_node, weight="weight")[0]

            inaccuracy_penalty = 0
            for src in source_candidates:
                if not st.is_settled():
                    for rout in point_routes[src]:
                        if st not in rou_lists[rout]:
                            inaccuracy_penalty += 1000
                    if rou in point_routes[src]:
                        inaccuracy_penalty += 1000
                for tgt in target_candidates:
                    if not nb.is_settled():
                        for rout in point_routes[tgt]:
                            if nb not in rou_lists[rout]:
                                inaccuracy_penalty += 1000
                        if rou in point_routes[tgt]:
                            inaccuracy_penalty += 1000
                    sp = nx.bidirectional_dijkstra(grid_graph_copy, source=src, target=tgt, weight="weight")[1]
                    length = nx.bidirectional_dijkstra(grid_graph_copy, source=src, target=tgt, weight="weight")[0]
                    penalty = geo_penalty * (math.sqrt((src[0] - st_node[0]) ** 2 + (src[1] - st_node[1]) ** 2)
                                             + math.sqrt((tgt[0] - nb_node[0]) ** 2 + (tgt[1] - nb_node[1]) ** 2))
                    if length + penalty + inaccuracy_penalty < min_length:
                        min_length = length + penalty + inaccuracy_penalty
                        final_src = src
                        final_tgt = tgt
                        min_sp = sp

            if final_src != st_node:
                st.set_coods(final_src[0], final_src[1])
                stop_coods[st.get_id()] = st.get_coods()
                gri_graph.nodes[final_src]['stop_label'] = gri_graph.nodes[st_node]['stop_label']
                del stops[st_node]
                stops[final_src] = st
                gri_graph.nodes[st_node]['stop_label'] = ''
                gri_graph.nodes[st_node]['drawn'] = False
            gri_graph.nodes[final_src]['drawn'] = True

            if final_tgt != nb_node:
                nb.set_coods(final_tgt[0], final_tgt[1])
                stop_coods[nb.get_id()] = nb.get_coods()
                gri_graph.nodes[final_tgt]['stop_label'] = gri_graph.nodes[nb_node]['stop_label']
                del stops[nb_node]
                stops[final_tgt] = nb
                gri_graph.nodes[nb_node]['stop_label'] = ''
                gri_graph.nodes[nb_node]['drawn'] = False
            gri_graph.nodes[final_tgt]['drawn'] = True

            for (node_1, node_2) in zip(min_sp, min_sp[1:]):

                if gri_graph.edges[node_1, node_2]['e_type'] in ['h', 'v', 'd1', 'd2']:
                    point_routes[(node_1[0], node_1[1])] = point_routes[(node_1[0], node_1[1])] + [rou]
                    current_list = gri_graph.edges[node_1, node_2]['routes']
                    current_list += [rou]
                    gri_graph.edges[node_1, node_2]['routes'] = current_list
                    grid_graph_copy.edges[node_1, node_2]['weight'] -= 0.005

            # close sinks
            for node in min_sp:
                if gri_graph.nodes[node]['node_type'] == 'standard':
                    for i in range(8):
                        gri_graph.edges[node, (node[0], node[1], i)]['weight'] = 125 * bend_factor

            # close crossing edges
            if len(min_sp) >= 5:
                for k in range(2, len(min_sp) - 2, 2):
                    a = min_sp[k - 1][2]
                    b = min_sp[k + 1][2]
                    if a > b:
                        a, b = b, a
                    for i in range(8):
                        for j in range(1, 8 - i):
                            if (a <= i <= b) != (
                                    a <= i + j <= b) and i != a and i != b and i + j != a and i + j != b:
                                gri_graph.edges[(min_sp[k][0], min_sp[k][1], i),
                                                (min_sp[k][0], min_sp[k][1], i + j)]['weight'] \
                                    = 100 * bend_factor * abs(j - 4)

            # settle stops, re-open sinks
            st.settle()
            st_node = st.get_coods()
            # close stop to avoid loops
            for i in range(8):
                grid_graph_copy.edges[st_node, (st_node[0], st_node[1], i)]['weight'] = 1250 * bend_factor
                for j in range(1, 8 - i):
                    grid_graph_copy.edges[(st_node[0], st_node[1], i), (st_node[0], st_node[1], i + j)]['weight'] \
                        = 1000 * bend_factor * abs(j - 4)

            if not nb.is_settled():
                nb_node = nb.get_coods()
                for i in range(8):
                    gri_graph.edges[nb_node, (nb_node[0], nb_node[1], i)]['weight'] = 3 * bend_factor
            nb.settle()

        cnt += 1
        print("Processed route {} of {}".format(cnt, len(rou_lists)))

    return gri_graph, stop_coods


def get_candidates(grid_graph, stops, st, neighbor, st_node, nb_node, min_frac, search_radius, threshold):
    source_candidates = [st_node]
    target_candidates = [nb_node]

    if not st.is_settled():

        alt_nodes = []
        a = - search_radius
        while a <= search_radius:
            b = - search_radius
            while b <= search_radius:
                if (a != 0 or b != 0) and (st_node[0] + a, st_node[1] + b) in grid_graph.nodes\
                        and (st_node[0] + a, st_node[1] + b)\
                        not in [st.get_coods() for st in stops.values() if st.is_settled()]:
                    alt_nodes.append((st_node[0] + a, st_node[1] + b))
                b += min_frac
            a += min_frac

        for node in alt_nodes:
            if grid_graph.nodes[node]['node_type'] == 'standard':
                source_distance = math.sqrt((st_node[0] - node[0]) ** 2 + (st_node[1] - node[1]) ** 2)
                target_distance = math.sqrt((nb_node[0] - node[0]) ** 2 + (nb_node[1] - node[1]) ** 2)
                if source_distance < target_distance and source_distance <= threshold:
                    source_candidates.append(node)
                elif target_distance <= threshold and not neighbor.is_settled():
                    target_candidates.append(node)

    if not neighbor.is_settled():

        alt_nodes = []
        a = - search_radius
        while a <= search_radius:
            b = - search_radius
            while b <= search_radius:
                if (a != 0 or b != 0) and (nb_node[0] + a, nb_node[1] + b) and (nb_node[0] + a, nb_node[1] + b)\
                        in grid_graph.nodes and (nb_node[0] + a, nb_node[1] + b)\
                        not in [st.get_coods() for st in stops.values() if st.is_settled()]:
                    alt_nodes.append((nb_node[0] + a, nb_node[1] + b))
                b += min_frac
            a += min_frac

        for node in alt_nodes:
            if grid_graph.nodes[node]['node_type'] == 'standard':
                source_distance = math.sqrt((st_node[0] - node[0]) ** 2 + (st_node[1] - node[1]) ** 2)
                target_distance = math.sqrt((nb_node[0] - node[0]) ** 2 + (nb_node[1] - node[1]) ** 2)
                if target_distance < source_distance and target_distance <= threshold:
                    target_candidates.append(node)
                elif source_distance <= threshold and not st.is_settled():
                    source_candidates.append(node)

    return source_candidates, target_candidates


def geodesic_dists(grid_graph, stops, skelet_graph):
    geo_dists = {}
    i = 0
    for st in [st for st in stops.keys() if grid_graph.nodes[st]['drawn']]:
        dist_sum = 0
        for nb in [st for st in stops.keys() if grid_graph.nodes[st]['drawn']]:
            dist_sum += nx.bidirectional_dijkstra(skelet_graph, source=st, target=nb, weight='weight')[0]
        geo_dists[st] = dist_sum
        i += 1
        print("Processed stop {} of {}".format(i, len([st for st in stops.keys() if grid_graph.nodes[st]['drawn']])))
    return geo_dists


if __name__ == '__main__':
    GRIDS, SCALE, SEARCH_RADIUS, BEND_FACTOR, GEO_PENALTY = [float(x) for x in sys.argv[1:]]
    main(GRIDS, SCALE, SEARCH_RADIUS, BEND_FACTOR, GEO_PENALTY)
