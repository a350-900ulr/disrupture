# scratchpad file

import networkx as nx
from TransitGraph import TransitGraph as tg
from copy import deepcopy

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







from TransitGraph import TransitGraph as tg

net = tg()

net.add_edge('test', 'test2', line=['U4'])


net.has_edge('test', 'test2')
net.has_edge('test2', 'test')


print(net['test']['test2'])
net['test']['test2']['line'].append('U3')
print(net['test']['test2'])




from copy import deepcopy
def minimize_changes(possible_lines: list[set[str]]) -> list[str]:
	
	def strip_extra_lines(possible_lines_inner) -> list[set[str]]:
		# add first segment to total lines
		total_lines = [possible_lines_inner[0]]
		# go through the rest of the journey
		for next_lines in possible_lines_inner[1:]:
			# if the next segment has different lines
			if total_lines[-1] != next_lines:
				# 1st create a duplicate of the current lines for reconsideration
				total_lines.append(deepcopy(total_lines[-1]))
				
				# create a duplicate of that for iteration
				considered_lines = deepcopy(total_lines[-1])
				
				# delete any that do not appear in the next segment
				for line in considered_lines:
					if line not in next_lines:
						total_lines[-1].remove(line)
				
				# if there are no continued lines, add all lines from the next segment
				if len(total_lines[-1]) == 0:
					total_lines[-1] = next_lines

		return total_lines

	input_path = strip_extra_lines(possible_lines)
	input_path.reverse()
	input_path = strip_extra_lines(input_path)
	input_path.reverse()
	
	condensed_path = []
	for line in input_path:
		#print(condensed_path)
		assert len(line) == 1, f'this should not happen but just incase'
		# extra single line from set
		next_line = next(iter(line))
		# add if not already there
	
		if len(condensed_path) == 0:
			condensed_path.append(next_line)
		else:
			if condensed_path[-1] != next_line:
				condensed_path.append(next_line)
		
	return condensed_path
	
	

input_list = [
	{'2', '10', '60'},
	{'2', '10', '60'},
	{'2', '52', '60'},
	{'2', '52', '60'},
	{'2', '6', '18'},
	{'2', '6', '18'},
	{'2', '18'},
	{'2', '18', '4'},
	{'2', '18'},
	{'18', '1'},
	{'18', '1'},
	{'1'}
]

output = minimize_changes(input_list)
print(output)


input_list = [
	{'10', '60'},
	{'10', '60'},
	{'52', '60'},
	{'52', '60'},
	{'6', '18'},
	{'6', '18'},
	{'18'},
	{'18', '4'},
	{'18'},
	{'18', '1'},
	{'18', '1'},
	{'1'}
]
print(minimize_changes(input_list))



from TransitGraph import TransitGraph as tg
net = tg()
print(net.segment_wait_time({'S2', 'S8'}))