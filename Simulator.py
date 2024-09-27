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
		
	def generate_journeys(self) -> None:
		"""
		Simulates a `self.journey_count` number of journeys with randomly initialized origin &
		target destinations. This information is stored in the `self.journeys` dictionary.
		"""
		
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
			
	def disrupt(self, station_to_close: str, print_unreachable: bool = False) -> None:
		"""
		Simulates a disruption & adds the new trip details to the `self.journeys` dictionary.
		:param station_to_close: Name of the station to be deleted from the transit graph
			`self.net`. All adjacent edges are also deleted.
		:param print_unreachable: Print out the origin & target of journeys that are no longer
			possible due to the disruption.
		:return:
		"""
		if not self.net.has_node(station_to_close):
			find_possible_match(station_to_close, list(self.net.nodes))
			quit()
		
		# if journeys have not been simulated yet, run it
		if len(self.journeys) == 0:
			print('Journeys have not been simulated yet, doing now')
			self.generate_journeys()
		
		self.net.remove_node(station_to_close)
		
		for journey in tqdm(self.journeys, desc='Simulating disruption'):
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
		
		