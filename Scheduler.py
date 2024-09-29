from itertools import combinations
from Simulator import Simulator as Sim
from copy import deepcopy
import sys
def min_index_with_none(input_list: list):
	min_value = sys.maxsize
	min_index = -1
	for index, value in enumerate(input_list):
		if value < min_value:
			min_value = value
			min_index = index
	
	return min_index
	
def schedule_disruptions(
	disruptions: list[str | list[str | set]], max_at_once: int = 2, resolution: int = 100
):
	
	assert 1 < max_at_once < len(disruptions)
	
	# get all combinations of disruptions
	comb = list(combinations(disruptions, max_at_once))
	print(f'# of combinations to test: {len(comb)}')
	
	sim = Sim(journey_count=resolution)
	
	# collect scores of each pair
	scores = []
	
	for combo in comb:
		sim.reset_graph()
		sim.simulate_journeys()
		for disruption in combo:
			sim.disrupt(disruption)
		sim.simulate_disruption()
		scores.append(sim.get_stats()['score'])
	
	# start collecting indices of combinations with best scores
	best_indices = [scores.index(min(scores))]
	
	# remove the best tuple along with any others that contain the same values
	disruptions_left = deepcopy(comb)
	scores_left = deepcopy(scores)
	removal_indices = []
	for index, disruption in enumerate(disruptions_left):
		if disruption is None:
			continue
		for best_disrupt in comb[best_indices[0]]:  # maybe -1 instead?
			if best_disrupt in disruption:
				removal_indices.append(index)
				# if this disruption contains any of the best_disrupt stations, the rest of this
				# disruption does not need to be checked
				break
	
	for removal_index in removal_indices:
		disruptions_left[removal_index] = None
		scores_left[removal_index] = None
	
	# find next best pair
	best_indices.append(min_index_with_none(scores_left))
	# ...
	
	
	
