# Rupture

A generalized transit planner for Vienna. Given a list of scheduled disruptions (such as station/track segment maintenance), this program will determine the optimal order of maintenance to cause the overall least disruption combined. 

All station data was acquired from https://citymapper.com/

# Example usage

This program uses Python version 3.12

The primary function of this program is scheduling maintenance via `Scheduler.schedule_disruptions()`, which takes in a list of disruptions. Disruptions can be in the following format:
1. `'station'`
	* Removes a station, including all adjacent lines
2. `['origin', 'target']`
	* List containing the origin & target names of the desired track segment to be removed.
3. `['origin', 'target', {lines...}]`
	* Same as before, except with the optional 3rd element in the list being a set containing only specific lines to
	  remove from the segment.

Below is an example of the most basic usage, which assumes that only 2 stations can be closed at once. This can be modified via the argument `max_at_once`:

```python
from Scheduler import schedule_disruptions

schedule_disruptions(['Schwedenplatz', 'Schottenring', 'Parlament', 'Volkstheater', 'Handelskai'])
```
Output: 
```
Recommended closure order:
('Schwedenplatz', 'Schottenring')
('Parlament', 'Handelskai')
Volkstheater
```

To get familiarized with other stations in Vienna along with what lines serve them, take a look at `Vienna_trains.png`.

# Other Functions

* Routing - via the class `TransitGraph`
	1. `print_fastest_path(origin, target)`
* Disruption stats - via the class `Simulator`
	1. `disrupt(disruption)`
		* This can be called multiple times to combine desired disruptions.
	2. `simulate_journeys(self)`
	3. `Simulator.get_stats()`
	4. `Simulator.plot_delay()`

More examples of using these functions are found in `Results.ipynb`
 

