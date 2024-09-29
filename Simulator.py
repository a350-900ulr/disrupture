import numpy as np
from FuzzyFunctions import find_possible_match
from TransitGraph import TransitGraph as TG
from random import sample
import networkx as nx
from tqdm import tqdm
from matplotlib import pyplot as plt


class Simulator:
	def __init__(self, journey_count: int = 1_000, loading_bars: bool = True):
		"""
		Handles simulation of many journeys in order to add a disruption & collect relevant
		statistics over single or multiple journeys.
		:param journey_count: # of journeys to simulate
		"""
		self.journey_count = journey_count
		self.net = TG()
		self.journeys = list(dict())
		
		self.removed_stations = []
		
		# flags
		self.disruption = False
		self.disruption_ran = False
		
		self.loading_bars = loading_bars
	
	def reset_graph(self, new_journey_count: int = None) -> None:
		"""
		Resets the graph to its initial state. Useful for undoing any simulated disruptions.
		This removes all currently simulated journeys & disruptions.
		:param new_journey_count: a new # of journeys to simulate
		"""
		if new_journey_count is not None:
			self.journey_count = new_journey_count
		self.net = TG()
		self.journeys = list()
		self.disruption = False
		self.disruption_ran = False
	
	def simulate_journeys(self) -> None:
		"""
		Simulates a `self.journey_count` number of journeys with randomly initialized origin &
		target destinations. This information is stored in the `self.journeys` dictionary.
		"""
		
		if len(self.journeys) != 0:
			print('Error: journeys already simulated. Reset graph before simulating again.')
			return
		
		iterator = tqdm(range(self.journey_count), desc='Simulating journeys') \
			if self.loading_bars \
			else range(self.journey_count)
	
		for _ in iterator:
			origin, target = sample(list(self.net.nodes), k=2)
			lines, time, stations = self.net.fastest_path(origin, target)
			self.journeys.append({
				'origin': origin,
				'target': target,
				'lines': lines,
				'time': time,
				'stations': stations
			})
			
	def disrupt(self, station: str | list[str | set]) -> None:
		"""
		Simulates a disruption & adds the new trip details to the `self.journeys` dictionary.
		:param station: Either a single string of the station name to be deleted from the
			transit graph `self.net` with all adjacent edges are also deleted, or a list
			containing the origin & target names of the desired segment to be deleted.
			An optional 3rd element in the list can be a set containing only specific lines to
			remove from the segment. If this is left empty, the entire segment is removed.
		"""
		
		if self.disruption_ran:
			print(
				'Error: Disruption has already been simulated. '
				'Reset graph before creating a new disruption.'
			)
			return
			
		# if journeys have not been simulated yet, run it
		if len(self.journeys) == 0:
			print('Journeys have not been simulated yet, doing now')
			self.simulate_journeys()
			
		if type(station) is str:
			self.disrupt_station(station)
		elif type(station) is list:
			assert len(station) in [2, 3], \
				'If given a list, only Origin & Target station can be supplied, ' \
				'with an optional set of lines'
			if len(station) == 3:
				for line in station[2]:
					assert type(line) is str, 'Lines to be canceled must be strings'
			self.disrupt_segment(*station)

		else:
			raise TypeError('Station must be either a string or a list of 2 strings')
		
	def disrupt_station(self, station_to_close: str) -> None:
		"""
		Called by `self.disrupt()`. Relevant docs are there.
		"""
		if not self.net.has_node(station_to_close):
			if station_to_close in self.removed_stations:
				print('Station already removed.')
			else:
				find_possible_match(station_to_close, list(self.net.nodes))
			return
		
		self.net.remove_node(station_to_close)
		self.removed_stations.append(station_to_close)
		self.disruption = True
	
	def disrupt_segment(self, origin, target, certain_lines: set = None) -> None:
		"""
		Called by `self.disrupt()`. Relevant docs are there.
		"""
		
		not_found_flag = False
		for station in [origin, target]:
			if not self.net.has_node(station):
				if station in self.removed_stations:
					print(f'Station {station} already removed, thus also this segment.')
					return
				else:
					find_possible_match(station, list(self.net.nodes))
					not_found_flag = True

		if not_found_flag:
			return
		
		if not self.net.has_edge(origin, target):
			print(f'Origin `{origin}` & Target `{target}` are not adjacent to eachother.')
			return
			
		if certain_lines is None:
			self.net.remove_edge(origin, target)
		else:
			for line in certain_lines:
				self.net[origin][target]['lines'].remove(line)
		
		self.disruption = True
		
	def simulate_disruption(self, print_unreachable: bool = False) -> None:
		"""
		To re-run all journeys after a `self.disrupt()`
		:param print_unreachable: Print out the origin & target of journeys that are no longer
			possible due to the disruption.
		:param loading_bar: Whether to use a tqdm loading bar. This is not used when scheduling
		"""
		
		if not self.disruption:
			print('Error: Disrupt a station/segment before simulating it.')
			return
		
		iterator = tqdm(self.journeys, desc='Simulating disruption') \
			if self.loading_bars \
			else self.journeys
		
		for journey in iterator:
			try:
				lines, time, stations = self.net.fastest_path(
					journey['origin'], journey['target'], sim_mode=True
				)
				journey['lines_new'] = lines
				journey['time_new'] = time
				journey['stations_new'] = stations
			except nx.exception.NodeNotFound:
				if print_unreachable:
					print(
						f'Journey from {journey["origin"]} to {journey["target"]} not possible'
					)
				continue
			except nx.exception.NetworkXNoPath:
				if print_unreachable:
					print(
						f'Journey from {journey["origin"]} to {journey["target"]} '
						f'is no longer reachable'
					)
				continue
		
		self.disruption_ran = True
		
	def get_stats(self) -> dict:
		"""
		delay, delay as percent,
		:return:
		"""
		if not self.disruption_ran:
			print('Error: No simulation of disruption was found')
			return dict()
		
		canceled = 0
		faster = 0
		delayed = 0
		delays = []
		delays_percent = []
		for index, journey in enumerate(self.journeys):
			if 'time_new' in journey:
				if journey['time_new'] != journey['time']:
					if journey['time_new'] < journey['time']:
						faster += 1
					else:
						delayed += 1
					delays.append(journey['time_new'] - journey['time'])
					delays_percent.append((journey['time_new']*100) / journey['time'] - 100)
			else:
				canceled += 1

		return {
			'score': canceled * 100 + delayed * np.mean(delays_percent),
			'journeys_delayed': delayed,
			'journeys_faster': faster,
			'journeys_canceled': canceled,
			'journeys_total': self.journey_count,
			'delay_times': {
				'min': min(delays),
				'median': np.median(delays),
				'mean': np.mean(delays),
				'max': max(delays),
			},
			'delay_times_perc': {
				'min': min(delays_percent),
				'median': np.median(delays_percent),
				'mean': np.mean(delays_percent),
				'max': max(delays_percent),
			}
		}
	
	def plot_delay(self, affected_only: bool = True) -> None:
		"""
		Plots 2 histograms of the previous & new travel times of the simulated journeys.
		:param affected_only: Only plot journeys affected by the disruption.
		"""
		if not self.disruption_ran:
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
		
		