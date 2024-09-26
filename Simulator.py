from TransitGraph import TransitGraph as TG

# either calculate only by number of affected routes or all?
def get_disruption_stats(station: str, simulated_runs: int = 1_000):
	for i in range(simulated_runs):
		...