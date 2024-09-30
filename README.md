# Rupture

A transit planner for Vienna. If you are not already familiar with the trains in Vienna, take a look at `Vienna_trains.png`. 

All station data was acquired from https://citymapper.com/

# Functions

1. Routing - 
	1. `TransitGraph.print_fastest_path(origin, target)`
2. Disruption stats - 
	1. `Simulator.disrupt(disruption)` &/or `Simulator.disrupt(disruption)` for segments, lines are optional. Disruptions can be in the following format:
		1. 'station'
		2. ['origin', 'target']
		3. ['origin', 'target', {lines...}]
	2. `Simulator.get_stats()`
	3. `Simulator.plot_delay()`
3. Scheduling maintenance
	1. `Scheduler.schedule_disruptions([disruptions...])`, with a disruption being in the same format

For more details on functions & their arguments, view the respective docs. 

# Example usage

This program uses Python version 3.12

Examples of using the various classes are found in `Results.ipynb`