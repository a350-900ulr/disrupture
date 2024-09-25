
import networkx
from os import listdir
from os.path import isfile, join

class TransitGraph(networkx.Graph):
	travel_times = {
		'tram': 2,
		'trolley': 2,
		'metro': 2,
		'commuter': 2
	}
	
	def load_default_graph(self, line_folder: str = 'lines'):

		files = listdir(line_folder)
		
		###########################
		
		for file in files:
			with open(file, 'r') as file:
				for line in file:
					line_name, stations = line.strip().split(':', 1)
					
					station_list = [station.strip() for station in stations.split(',')]
					stations_dict[line_name.strip()] = station_list
			
	
	def add_lines(self, line_name: str, stations: list[str], custom_type: str = None):
		
		if custom_type is None:
			match line_name[0]:
				case 'U':
					transit_time = self.travel_times['metro']
				case 'S':
					transit_time = self.travel_times['commuter']
				case _ if line_name.isdigit():
					transit_time = self.travel_times['tram']
				case _:
					raise ValueError(f'Could not automatically determine type of {line_name}')
		else:
			transit_time = self.travel_times[custom_type]

		for index, station in enumerate(stations[:-1]):

			self.add_edge(
				station,
				stations[index + 1],
				line=line_name,
				weight=transit_time
			)
	
	def fastest_path(self, source, target):
		path = networkx.shortest_path(self, source=source, target=target, weight='weight')
		print(path)
		# total_time = 0
		# prev_line = None
		#
		# for i in range(len(path) - 1):
		# 	edge_data = self.get_edge_data(path[i], path[i + 1])
		# 	travel_time = edge_data['weight']
		#
		# 	current_line = edge_data['line']
		# 	if prev_line != current_line:
		# 		if current_line == 'U4' or current_line == 'U6':
		# 			travel_time += 3
		# 		elif current_line == 'S50':
		# 			travel_time += 10
		#
		# 	total_time += travel_time
		# 	prev_line = current_line
		#
		# return path, total_time


net = TransitGraph()
net.load_default_graph()

arr = listdir('lines')