import networkx as nx
from os import listdir
from re import match
from copy import deepcopy


class TransitGraph(nx.Graph):
	# Assumptions: all stations are bidirectional
	
	# Travel times between stations, assuming that all intervals are the same.
	travel_times = {
		'tram': 1.5,
		'trolley': 1.75,
		'metro': 2,
		'commuter': 3
	}
	
	# Typical interval during peak times
	wait_times = {
		'tram': 6,
		'trolley': 7.5,
		'metro': 3.5,
		'commuter': 30,
	}
	
	def __init__(self):
		super().__init__()
		self.load_default_graph()
	
	def load_default_graph(self, line_folder: str = 'lines'):
		
		for file_name in listdir(line_folder):
			line_name = file_name.split('.')[0]
			stations = []

			with open(f'{line_folder}/{file_name}', 'r') as file:
				for line in file:
					stations.append(line.strip())
			self.add_lines(line_name, stations)
		
	def add_lines(self,
		line_name: str,
		stations: list[str],
		custom_type: str = None,
		verbose: bool = False
	) -> None:
		if custom_type is None:
			line_type = self.detect_line_type(line_name)
		else:
			line_type = custom_type
	
		for index, station1 in enumerate(stations[:-1]):
			station2 = stations[index + 1]
			
			if self.has_edge(station1, station2):
				self[station1][station2]['lines'].add(line_name)
				'''
				If the line is of a different type than the existing value, convert it to the
				type with the shortest travel time. This is based on the same assumption that
				longer distance lines accommodate the distances of shorter distance lines when
				going into the city as it was most likely built for the shorter distance line.
				'''
				if line_type != self[station1][station2]['type']:
					if verbose:
						print(
							'\nMultiple lines of different type on the same edge detected.'
							f'\n\tExisting edge: {station1} - {station2}'
							f'\n\tExisting type: {self[station1][station2]['type']}'
							f'\n\tProposed type: {line_type}'
						)
					# if new line type is faster than previous
					if self.travel_times[line_type] < self[station1][station2]['travel_time']:
						self[station1][station2]['type'] = line_type
						self[station1][station2]['travel_time'] = self.travel_times[line_type]
			else:
				self.add_edge(
					station1,
					station2,
					lines={line_name},  # encapsulate in a set in case of shared lines
					type=line_type,
					travel_time=self.travel_times[line_type],
				)
	
	def detect_line_type(self, line_name: str) -> str:
		if match('^\\d{1,2}$', line_name) or line_name in ['D', 'O']:
			line_type = 'tram'
		elif line_name == 'BB':
			line_type = 'trolley'
		elif match('^U\\d$', line_name):
			line_type = 'metro'
		elif match('^S\\d{1,2}$', line_name) or line_name == 'Stammstrecke':
			line_type = 'commuter'
		else:
			raise ValueError(f'Could not automatically determine type of {line_name}')
		return line_type

	def fastest_path(self,
		source,
		target,
		paths_before_transfers: int = 6,
		print_results: bool = False,
		verbose: bool = False
	):
		"""
		Finds the fastest path between a source & target station.

		"""
		
		path_generator = nx.shortest_simple_paths(self, source, target, weight='travel_time')
		
		# get a certain amount of journeys using only travel_time weights
		top_paths: list[list[str]] = []

		for index, path in enumerate(path_generator):
			if index >= paths_before_transfers:
				break
			top_paths.append(path)
			
		
		# calculate transit times & get list of possible lines throughout the route
		total_times = []
		lines_in_paths = []
		for candidate_path in top_paths:
			
			lines_used: list[set[str]] = []
			current_time = 0
			
			# get initial segment line & transit times
			for index, station1 in enumerate(candidate_path[:-1]):
				station2 = candidate_path[index + 1]
				
				lines_used.append(self[station1][station2]['lines'])
				current_time += self[station1][station2]['travel_time']
			
			# get line series
			lines_condensed = self.minimize_changes(lines_used)
			lines_in_paths.append(lines_condensed)
			
			# calculate transfer times
			for segment in lines_condensed:
				# if there is only 1 line in that segment, simply add its wait time
				current_time += self.segment_wait_time(segment)
			
			total_times.append(current_time)
		
		fastest_index = total_times.index(min(total_times))
		

		return \
			lines_in_paths[fastest_index], \
			total_times[fastest_index], \
			top_paths[fastest_index]
			
	def print_fastest_path(self, source: str, target: str, paths_before_transfers: int = 6):
		lines, time, stations = self.fastest_path(source, target, paths_before_transfers)
		print(
			f'\nLines used: {lines}'
			f'\nCalculated travel time: {time}'
			f'\nStations: {stations}'
		)
	def minimize_changes(self, possible_lines: list[set[str]]) -> list[set[str]]:
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
		
		# final step to remove repeats
		output_path = [input_path[0]]
		for segment in input_path[1:]:
			if segment != output_path[-1]:
				output_path.append(segment)
		
		return output_path
	
	def segment_wait_time(self, lines: set):
		"""
		for ease of calculation, assume all trains alternate perfectly

		"""
		trains_per_hour = 0
		# count number of trains coming per hour
		for line in lines:
			trains_per_hour += (60 / self.wait_times[self.detect_line_type(line)])
		
		return 30 / trains_per_hour


net = TransitGraph()
net.load_default_graph()
net.print_fastest_path('Radetzkyplatz', 'Karlsplatz')