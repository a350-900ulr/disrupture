from itertools import combinations
from Simulator import Simulator as Sim
from copy import deepcopy
import sys

	
	
def schedule_disruptions(
	disruptions: list[str | list[str | set]], max_at_once: int = 2, resolution: int = 100
):
	def min_index_with_none(input_list: list):
		min_value = sys.maxsize
		min_index = -1
		for i, value in enumerate(input_list):
			if value is not None and value < min_value:
				min_value = value
				min_index = i
		
		return min_index
	
	assert 1 < max_at_once < len(disruptions)
	
	# get all combinations of disruptions
	comb = list(combinations(disruptions, max_at_once))
	print(f'# of combinations to test: {len(comb)}')
	
	sim = Sim(journey_count=resolution)
	
	# collect scores of each pair
	scores = []
	
	for combo in comb:
		# sim.reset_graph()
		# sim.simulate_journeys()
		# for disruption in combo:
		# 	sim.disrupt(disruption)
		# sim.simulate_disruption()
		# scores.append(sim.get_stats()['score'])
		scores.append(sum([int(x) for x in combo]))
		
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


schedule_disruptions(['20', '7', '2', '23', '15', '8', '4'], 2)
