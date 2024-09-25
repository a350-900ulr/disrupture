import networkx as nx
from TransitGraph import TransitGraph as tg

net = tg()

net.add_edge('test', 'test2')

net.global_var('bepis', 5)
net.travel_times

G = nx.Graph()

U4_stations = [
	'Huetteldorf',
	'Ober St Veit',
	'Unter St. Veit',
	'Braunschweiggasse',
	'Hietzing',
	'Schoenbrunn',
	'Meidling Hauptstrasse',
	'Laengenfeldgasse',
]

U6_stations = [
	'Laengenfeldgasse',
	'Gumpendorferstrasse',
	'Westbahnhof'
]

S50_stations = [
	'Huetteldorf',
	'Penzing',
	'Westbahnhof'
]

stations_dict = {}

with open('stations_test.txt', 'r') as file:
	for line in file:
		line_name, stations = line.strip().split(':', 1)
		station_list = [station.strip() for station in stations.split(',')]
		stations_dict[line_name.strip()] = station_list

#print(stations_dict)



def add_edges_with_penalty(graph, stations, line, penalty):
	for index, station in enumerate(stations[:-1]):
		# Travel time between stations_test.txt is 1 minute
		graph.add_edge(
			station,
			stations[index + 1],
			weight=1, line=line
		)

add_edges_with_penalty(G, U4_stations, 'U4', penalty=3)
add_edges_with_penalty(G, U6_stations, 'U6', penalty=3)
add_edges_with_penalty(G, S50_stations, 'S50', penalty=10)

# calculate shortest path with transfer penalties
# make this actually work
def shortest_path_with_transfer_penalty(graph, source, target):
	path = nx.shortest_path(graph, source=source, target=target, weight='weight')
	total_time = 0
	prev_line = None
	
	for i in range(len(path) - 1):
		edge_data = graph.get_edge_data(path[i], path[i + 1])
		travel_time = edge_data['weight']
		
		# transfer penatly
		current_line = edge_data['line']
		if prev_line != current_line:
			# starting anew
			if current_line == 'U4' or current_line == 'U6':
				travel_time += 3
			elif current_line == 'S50':
				travel_time += 10
		
		total_time += travel_time
		prev_line = current_line
	
	return path, total_time


source = 'Schoenbrunn'
target = 'Westbahnhof'

path, total_time = shortest_path_with_transfer_penalty(G, source, target)

print(f"Fastest route from {source} to {target}:", path)
print(f"Total travel time: {total_time} minutes")


