import networkx as nx
from os import listdir
from re import match
from copy import deepcopy
from FuzzyFunctions import find_possible_match


class TransitGraph(nx.Graph):
	...
	'''
	Travel times between stations by type of line. This assumes an equal distance between all
	stations. If multiple lines of different types go through the same edge, the shortest time
	is taken. This is explained further in `self.add_lines`.
	'''
	travel_times = {
		'tram': 1.5,
		'trolley': 1.75,
		'metro': 2,
		'commuter': 3
	}
	
	'''
	Typical intervals of each line type during peak times. This assumes that all lines of a
	specific type have the same interval. An exception dictionary is created below this, which
	is evaluated in `self.segment_wait_time`.
	'''
	wait_times = {
		'tram': 6,
		'trolley': 7.5,
		'metro': 3.5,
		'commuter': 30,
	}
	wait_times_exceptions = {
		'S45': 10
	}
	
	def __init__(self, paths_before_transfers: int = 10, verbose_loading: bool = False):
		"""
		An extension of the networkx `Graph` class, with some extra methods that pertain to a
		transit network. All lines are assumed to be fully bidirectional, meaning no one-way
		stops.
		:param paths_before_transfers: The number of paths to consider before calculating the
			transfer times. This is because a journey could become longer than expected due to
			waiting for lower frequency lines. The fastest line among the initial paths is
			returned after this is calculated
		:param verbose_loading: Print out line conflict types when loading default graph.
		"""
		super().__init__()
		self.load_default_graph(verbose=verbose_loading)
		self.paths_before_transfers = paths_before_transfers
	
	def load_default_graph(self, line_folder: str = 'lines', verbose: bool = False) -> None:
		"""
		Populates the graph. Each line needs a file in the following format:
		
		*
			The name of the file is simply line followed by '.txt'. The names supported by
			automatic line type detection are implemented in `self.detect_line_type`.
			
		* The contents must be the name of each station (direction does not matter), 1 per line.
		
		:param line_folder: Name of the folder containing the line files. No subfolders or extra
			files are allowed.
		:param verbose: Print out line conflict types when loading default graph.
		"""
		
		for file_name in listdir(line_folder):
			line_name = file_name.split('.')[0]
			stations = []

			with open(f'{line_folder}/{file_name}', 'r') as file:
				for line in file:
					stations.append(line.strip())
			self.add_lines(line_name, stations, verbose=verbose)
		
	def add_lines(self,
		line_name: str,
		stations: list[str],
		custom_type: str = None,
		verbose: bool = False
	) -> None:
		"""
		Adds a line to the transit graph, automatically handling edges serviced by multiple
		lines. Each edge has the following attributes:
		
		* lines : A set of the lines servicing this segment.
		
		*
			type : The type of line mainly servicing this. Only the type with the shortest
			travel time is stored. This is explained further in the code.
			
		* travel_time : The shortest travel time of all lines that service the segment.
		
		:param line_name: The name of the line as a string
		:param stations: The 2 stations connected by this line
		:param custom_type: A manually specified type of line that must be implemented in
			`self.travel_times` & `self.wait_times`
		:param verbose: Print out any conflicts of multiple line types on the same line
		"""
		
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
				type with the shortest travel time. This is based on the assumption that longer
				distance lines (such as commuter lines) accommodate the distances of shorter
				distance lines (such as metros) when going into more populated areas. Although
				this happens both ways, since this graph is designed around a transit system
				within a heavily populated city, it is more likely that a segment is built for
				shorter distance lines. Thus for ease of calculation, the shorter travel time is
				used for all lines in a segment.
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
					# encapsulate in a set in case of shared lines to remove possible duplicates
					lines={line_name},
					type=line_type,
					travel_time=self.travel_times[line_type],
				)
	
	def detect_line_type(self, line_name: str) -> str:
		"""
		Automatically determine the type of line based on the name. The supported names are
		described in comments above the respective condition in the code.
		:param line_name: A string of the line name
		:return: Detected line type, the details of which should be implemented by
			`self.travel_times` & `self.wait_times`
		:raise ValueError: If the line type cannot be determined.
		"""
		
		# 1 or 2 numbers, or the letter lines "D" & "O"
		if match('^\\d{1,2}$', line_name) or line_name in ['D', 'O']:
			line_type = 'tram'
		# Badnerbahn
		elif line_name == 'BB':
			line_type = 'trolley'
		# Capital "U" followed by 1 number
		elif match('^U\\d$', line_name):
			line_type = 'metro'
		# Capital "S" followed by 1 or 2 numbers, or the Stammstrecke (used in testing)
		elif match('^S\\d{1,2}$', line_name) or line_name == 'Stammstrecke':
			line_type = 'commuter'
		else:
			raise ValueError(f'Could not automatically determine type of {line_name}')
		return line_type
	
	def fastest_paths(self,
		source: str,
		target: str,
	) -> tuple[list[list[set[str]]], list[float], list[list[str]]]:
		"""
		Internal helper function called by `self.fastest_path`, see there for docs
		"""
		
		path_generator = nx.shortest_simple_paths(self, source, target, weight='travel_time')
		
		# get a certain amount of journeys using only travel_time weights
		top_paths: list[list[str]] = []
		for index, path in enumerate(path_generator):
			if index >= self.paths_before_transfers:
				break
			top_paths.append(path)
		
		# calculate transfer times & also get a list of possible lines throughout the route
		total_times = []  # same length as `top_paths`
		lines_in_paths = []  # lines used in each candidate journey
		for candidate_path in top_paths:
			lines_possible: list[set[str]] = []
			current_time = 0
			
			# get initial segment line & transit times
			for index, station1 in enumerate(candidate_path[:-1]):
				station2 = candidate_path[index + 1]
				
				lines_possible.append(self[station1][station2]['lines'])
				current_time += self[station1][station2]['travel_time']
			
			# condensed
			lines_used = self.minimize_changes(lines_possible)
			lines_in_paths.append(lines_used)
			
			# calculate transfer times
			previous_type = None
			for line in lines_used:
				'''
				Although technically a line can be of multiple types, we take the 1st one
				as a simplification. The conflicts themselves can be seen by running
				
				load_default_graph(verbose_loading=True)
				
				TODO: see specific behavior of this
				'''
				current_type = self.detect_line_type(next(iter(line)))
				
				if previous_type is None:
					previous_type = current_type
				else:
					# impose transfer penalty
					if current_type != previous_type:
						current_time += 2
						previous_type = current_type
					else:
						current_time += 1
				
				current_time += self.segment_wait_time(line)
			
			total_times.append(current_time)
			
		return lines_in_paths, total_times, top_paths
		
	def fastest_path(self,
		source: str,
		target: str,
		sim_mode: bool = False
	) -> tuple[list[set[str]], float, list[str]]:
		"""
		Finds the fastest path between a source & target station. This partially uses the
		implementation `networkx.shortest_simple_paths` by taking the travel_time for a segment
		as the weight. The transfer times between lines is then manually calculated.
		
		:param source: The source station
		:param target: The target station
		:param sim_mode: Internal parameter for running simulations, which skips checking
			possible matches for missing nodes.
		:return: A tuple of the following information:
			(1) The lines used in the journey as a list of sets.
			(2) The calculated total time for this journey.
			(3) The list of stations visited in order.
		"""

		if not sim_mode:
			if not self.has_node(source):
				find_possible_match(source, list(self.nodes))
				return list(), float(), list()
			if not self.has_node(target):
				find_possible_match(target, list(self.nodes))
				return list(), float(), list()
		
		lines_in_paths, total_times, top_paths = self.fastest_paths(source, target)
		
		fastest_index = total_times.index(min(total_times))
		
		return \
			lines_in_paths[fastest_index], \
			total_times[fastest_index], \
			top_paths[fastest_index]
			
	def print_fastest_path(self, source: str, target: str, paths_before_transfers: int = 6):
		"""
		Helper function to print out results of `self.fastest_path`. The arguments are the same
		as this function.
		"""
		lines, time, stations = self.fastest_path(source, target)
		print(
			f'\nLines used: {lines}'
			f'\nCalculated travel time: {time}'
			f'\nStations: {stations}'
		)
		
	def minimize_changes(self, possible_lines: list[set[str]]) -> list[set[str]]:
		"""
		Helper function that takes all available lines for a given route & determines the ideal
		route with the least # of transfers.
		:param possible_lines: A list of sets showing the available lines at each station.
		:return: A (usually shorter) list in the same format, but only containing the ideal lines.
		"""
		def strip_extra_lines(possible_lines_inner: list[set[str]]) -> list[set[str]]:
			"""
			Removes unnecessary lines by traversing the list in a single direction & keeping
			only the lines serving the longest continuous segment.
			"""
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
		
		# remove unnecessary lines in both directions
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
	
	def segment_wait_time(self, lines: set) -> float:
		"""
		Calculates a possible average wait time given the lines that serve a segment. For ease
		of calculation, trains with the same interval are assumed to alternate perfectly, which
		is the case for commuter services in Vienna. For example, if 2 trains come every 30
		minutes, the maximum expected wait time is 15 minutes.
		:param lines: A set showing the available lines at some station.
		:return: A number indicating the average wait time
		"""
		trains_per_hour = 0
		# count number of trains coming per hour
		for line in lines:
			if line in self.wait_times_exceptions:
				wait = self.wait_times_exceptions[line]
			else:
				wait = self.wait_times[self.detect_line_type(line)]
				
			trains_per_hour += (60 / wait)
		
		# half the wait time (30 instead of 60) to get the average instead of maximum
		return 30 / trains_per_hour

