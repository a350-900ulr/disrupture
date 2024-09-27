from TransitGraph import TransitGraph as TG
from random import sample
import networkx as nx


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
		
	def generate_journeys(self):
		for i in range(self.journey_count):
			origin, target = sample(self.stations, k=2)
			lines, time, stations = self.net.fastest_path(origin, target)
			self.journeys.append({
				'origin': origin,
				'target': target,
				'lines': lines,
				'time': time,
				'stations': stations
			})
			
	def disrupt(self, station_to_close: str, print_unreachable: bool = False) -> int:
		
		# if journeys have not been simulated yet, run it
		if len(self.journeys) == 0:
			self.generate_journeys()
		
		self.net.remove_node(station_to_close)
		
		unreachable = 0
		for journey in self.journeys:
			#print(f'Journey from {journey["origin"]} to {journey["target"]}')
			if station_to_close in [journey['origin'], journey['target']]:
				unreachable += 1
				if print_unreachable:
					print(f'Journey from {journey["origin"]} to {journey["target"]} not possible')
				continue
			
			try:
				lines, time, stations = self.net.fastest_path(
					journey['origin'], journey['target']
				)
				journey['lines_new'] = lines
				journey['time_new'] = time
				journey['stations_new'] = stations
			except nx.exception.NetworkXNoPath:
				unreachable += 1
				if print_unreachable:
					print(f'Journey from {journey["origin"]} to {journey["target"]} not possible')
				continue
				
		return unreachable

