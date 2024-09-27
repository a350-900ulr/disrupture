from TransitGraph import TransitGraph as TG
from random import sample


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
			
	def get_disruption_stats(self, station: str, simulated_runs: int = 1_000):
		for i in range(simulated_runs):
			...