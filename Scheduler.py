from itertools import combinations
from Simulator import Simulator as Sim
from copy import deepcopy
from sys import maxsize
from tqdm import tqdm


def schedule_disruptions(
	disruptions: list[str | list[str | set]], max_at_once: int = 2, resolution: int = 100
):
	"""
	Takes in a list of disruptions & runs through every combination calculating the score.
	Each combination is then print from lowest to highest score.
	:param disruptions: For more detailed description of the disruption format, see
		`Simulator.disrupt(station)`
	:param max_at_once: # of disruptions allowed in each combination.
	:param resolution: # of journeys to simulate when calculating the disruption score
	:return:
	"""
	
	def min_index_with_none(input_list: list):
		"""
		Finds the smallest number in a list & returns its index.
		"""
		min_value = maxsize
		min_index = -1
		for i, value in enumerate(input_list):
			if value is not None and value < min_value:
				min_value = value
				min_index = i
		
		return min_index
	
	assert 1 < max_at_once < len(disruptions)
	
	# get all combinations of disruptions
	comb = list(combinations(disruptions, max_at_once))
	
	sim = Sim(journey_count=resolution, loading_bars=False)
	
	# collect scores of each pair
	scores = []
	
	for combo in tqdm(comb, desc='Running combinations'):
		sim.reset_graph()
		sim.simulate_journeys()
		for disruption in combo:
			sim.disrupt(disruption)
		sim.simulate_disruption()
		scores.append(sim.get_stats()['score'])
		
	disruptions_left = deepcopy(disruptions)
	disrupt_combos_left = deepcopy(comb)
	scores_left = deepcopy(scores)
	
	best_indices = []
	
	# find next best pair
	while sum([0 if x is None else 1 for x in disrupt_combos_left]) > 0:
		# start collecting indices of combinations with best scores
		best_indices.append(min_index_with_none(scores_left))
		
		# remove disruptions in the best disruption combination from the total list
		for best_disrupt in comb[best_indices[-1]]:
			disruptions_left.remove(best_disrupt)
		
		# remove the best tuple along with any others that contain the same values
		removal_indices = []
		for index, disruption in enumerate(disrupt_combos_left):
			if disruption is None:
				continue
				
			for best_disrupt in comb[best_indices[-1]]:  # maybe -1 instead?
				if best_disrupt in disruption:
					removal_indices.append(index)
					# if this disruption contains any of the best_disrupt stations, the rest of this
					# disruption does not need to be checked
					break
			
		for removal_index in removal_indices:
			disrupt_combos_left[removal_index] = None
			scores_left[removal_index] = None
	
	for index in best_indices:
		print(comb[index])
		
	for disruption in disruptions_left:
		print(disruption)