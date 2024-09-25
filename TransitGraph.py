import networkx as nx
from os import listdir
from re import match


class TransitGraph(nx.Graph):
	# between stations
	travel_times = {
		'tram': 2,
		'trolley': 2,
		'metro': 2,
		'commuter': 2
	}
	
	
	def load_default_graph(self, line_folder: str = 'lines'):
		
		for file_name in listdir(line_folder):
			line_name = file_name.split('.')[0]
			stations = []

			with open(f'{line_folder}/{file_name}', 'r') as file:
				for line in file:
					stations.append(line.strip())
			self.add_lines(line_name, stations)
		
	def add_lines(self, line_name: str, stations: list[str], custom_type: str = None):
		if custom_type is None:
			line_type = self.detect_line_type(line_name)
		else:
			line_type = custom_type
	
		for index, station in enumerate(stations[:-1]):
			# TODO: if line already exist, append line to list of lines
			# also always make it a list
			self.add_edge(
				station,
				stations[index + 1],
				line=line_name,
				type=line_type,
				travel_time=self.travel_times[line_type]
			)
	
	def detect_line_type(self, line_name: str) -> str:
		if match('^\d{1,2}$', line_name):
			line_type = 'tram'
		elif match('^U\d$', line_name):
			line_type = 'metro'
		elif match('^S\d{1,2}$', line_name):
			line_type = 'commuter'
		elif line_name == 'Stammstrecke':  # manually added for testing, to be split later
			line_type = 'commuter'
		else:
			raise ValueError(f'Could not automatically determine type of {line_name}')
		return line_type

	def fastest_path(self, source, target, paths_before_transfers: int = 1):
		# find top k paths
		path_generator = nx.shortest_simple_paths(self, source, target, weight='travel_time')
		top_paths = []
		for index, path in enumerate(path_generator):
			if index >= paths_before_transfers:
				break
			top_paths.append(path)
		
		# add transfer weights
		
		# take top (mark if its ever different?)

	

net = TransitGraph()
net.load_default_graph()
net.fastest_path('Schönbrunn', 'Stephansplatz')
#arr = listdir('lines')