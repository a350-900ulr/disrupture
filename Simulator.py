from FuzzyFunctions import find_possible_match
from TransitGraph import TransitGraph as TG
from random import sample
import networkx as nx
from tqdm import tqdm
from matplotlib import pyplot as plt


class Simulator:
	def __init__(self, journey_count: int = 1_000):
		"""
		Handles simulation of many journeys in order to add a disruption & collect relevant
		statistics over single or multiple journeys.
		:param journey_count: # of journeys to simulate
		"""
		self.journey_count = journey_count
		self.net = TG()
		self.stations = list(self.net.nodes)
		self.journeys = list(dict())
		
		self.disrupted = False
	
	def reset_graph(self) -> None:
		"""
		Resets the graph to its initial state. Useful for undoing any simulated disruptions.
		This removes all currently simulated journeys & disruptions.
		"""
		self.net = TG()
		self.journeys = list(dict())
		self.disrupted = False
	
	def generate_journeys(self) -> None:
		"""
		Simulates a `self.journey_count` number of journeys with randomly initialized origin &
		target destinations. This information is stored in the `self.journeys` dictionary.
		"""
		
		if len(self.journeys) != 0:
			print('Warning: journeys already simulated. Overwriting existing journeys.')
		
		for _ in tqdm(range(self.journey_count), desc='Simulating journeys'):
			origin, target = sample(self.stations, k=2)
			lines, time, stations = self.net.fastest_path(origin, target)
			self.journeys.append({
				'origin': origin,
				'target': target,
				'lines': lines,
				'time': time,
				'stations': stations
			})
			
	def disrupt(
		self, station: str | list[str | set], print_unreachable: bool = False
	) -> None:
		"""
		Simulates a disruption & adds the new trip details to the `self.journeys` dictionary.
		:param station: Either a single string of the station name to be deleted from the
			transit graph `self.net` with all adjacent edges are also deleted, or a list
			containing the origin & target names of the desired segment to be deleted.
			An optional 3rd element in the list can be a set containing only specific lines to
			remove from the segment. If this is left empty, the entire segment is removed.
		:param print_unreachable: Print out the origin & target of journeys that are no longer
			possible due to the disruption.
		"""
		
		if self.disrupted:
			print('Warning: Disruption has already been simulated. Overwriting existing data.')
		
		# if journeys have not been simulated yet, run it
		if len(self.journeys) == 0:
			print('Journeys have not been simulated yet, doing now')
			self.generate_journeys()
			
		if type(station) is str:
			self.disrupt_station(station, print_unreachable)
		elif type(station) is list:
			match len(station):
				case 2:
					self.disrupt_segment(
						origin=station[0],
						target=station[1],
						print_unreachable=print_unreachable
					)
				case 3:
					self.disrupt_segment(
						origin=station[0],
						target=station[1],
						certain_lines=station[2],
						print_unreachable=print_unreachable
					)
				case _:
					print(
						'If given a list, only Origin & Target station can be supplied, '
						'with an optional set of lines'
					)
		else:
			raise TypeError('Station must be either a string or a list of 2 strings')
		
	def disrupt_station(self, station_to_close: str, print_unreachable: bool = False) -> None:
		"""
		Called by `self.disrupt()`. Relevant docs are there.
		"""
		if not self.net.has_node(station_to_close):
			find_possible_match(station_to_close, list(self.net.nodes))
			return
		
		self.net.remove_node(station_to_close)
		
		for journey in tqdm(self.journeys, desc='Simulating station disruption'):
			if station_to_close in [journey['origin'], journey['target']]:
				if print_unreachable:
					print(
						f'Journey from {journey["origin"]} to {journey["target"]} not possible'
					)
				continue
			
			try:
				lines, time, stations = self.net.fastest_path(
					journey['origin'], journey['target']
				)
				journey['lines_new'] = lines
				journey['time_new'] = time
				journey['stations_new'] = stations
			except nx.exception.NetworkXNoPath:
				if print_unreachable:
					print(
						f'Journey from {journey["origin"]} to {journey["target"]} '
						f'is no longer reachable'
					)
				continue
		self.disrupted = True
	
	def disrupt_segment(
		self, origin, target, certain_lines: set = None, print_unreachable: bool = False
	) -> None:
		"""
		Called by `self.disrupt()`. Relevant docs are there.
		"""
		
		not_found_flag = False
		for station in [origin, target]:
			if not self.net.has_node(station):
				find_possible_match(station, list(self.net.nodes))
				not_found_flag = True

		if not_found_flag:
			return
		
		if not self.net.has_edge(origin, target):
			print(f'Origin {origin} & Target {target} are not adjacent to eachother.')
			return
			
		if certain_lines is None:
			self.net.remove_edge(origin, target)
		else:
			for line in certain_lines:
				self.net[origin][target]['lines'].remove(line)
		
		for journey in tqdm(self.journeys, desc='Simulating segment disruption'):
			try:
				lines, time, stations = self.net.fastest_path(
					journey['origin'], journey['target']
				)
				journey['lines_new'] = lines
				journey['time_new'] = time
				journey['stations_new'] = stations
			except nx.exception.NetworkXNoPath:
				if print_unreachable:
					print(
						f'Journey from {journey["origin"]} to {journey["target"]} '
						f'is no longer reachable'
					)
				continue
				
		self.disrupted = True
		
	def get_stats(self) -> dict:
		"""
		delay, delay as percent,
		:return:
		"""
		if not self.disrupted:
			print('Error: No disruption was found')
			return dict()
		
		for journey in self.journeys:
			if 'time_new' in journey:
				...
	
	def plot_delay(self, affected_only: bool = True) -> None:
		if not self.disrupted:
			print('Error: No disruption was found')
			return
		
		time_old, time_new = [], []
		
		for journey in self.journeys:
			if affected_only:
				if 'time_new' in journey and journey['time'] != journey['time_new']:
					time_old.append(journey['time'])
					time_new.append(journey['time_new'])
			else:
				if 'time_new' in journey:
					time_old.append(journey['time'])
					time_new.append(journey['time_new'])

		plt.hist(time_old, bins=25, alpha=.5, label='old')
		plt.hist(time_new, bins=25, alpha=.5, label='new')
		plt.legend(loc='upper right')
		plt.show()


sim = Simulator(10)
sim.disrupt(['Schwedenplatz', 'Schottenring'])
sim.plot_delay()