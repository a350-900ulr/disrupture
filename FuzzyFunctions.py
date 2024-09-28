from difflib import SequenceMatcher


def detect_possible_duplicates(
	station_names: list[str], threshold: float = .8
) -> list[tuple[str, str]]:
	"""
	Detects possible duplicates in station names based on string similarity and naming conventions.
	:param station_names: list of all station names
	:param threshold: threshold for similarity, between 0 & 1
	:return: list of tuples, each containing two station names considered potential duplicates.
	"""
	duplicates = []
	for i in range(len(station_names)):
		for j in range(i + 1, len(station_names)):
			name1 = station_names[i]
			name2 = station_names[j]
			
			# basic containment check (one name contains the other)
			if name1 in name2 or name2 in name1:
				duplicates.append((name1, name2))
			
			# string similarity check using SequenceMatcher
			similarity = SequenceMatcher(None, name1, name2).ratio()
			if similarity >= threshold:
				duplicates.append((name1, name2))
	
	return duplicates


def find_possible_match(
	input_station: str,
	possible_stations: list[str],
	max_results: int = 10,
	threshold: float = .6
) -> None:
	"""
	Given an entire list of available stations, determine the most similar ones
	"""
	candidates = []
	
	input_station_lower = input_station.lower()
	input_station_lower = input_station_lower\
		.replace('str.', 'straße')\
		.replace('g.', 'gasse')
	
	for station in possible_stations:
		if input_station_lower in station.lower() or station.lower() in input_station_lower:
			candidates.append(station)
			
		similarity = SequenceMatcher(None, input_station_lower, station.lower()).ratio()
		if similarity >= threshold:
			candidates.append(station)

	print(f'Station {input_station} not found')
	
	if len(candidates) > 0:
		print('Did you mean:')
		for candidate in candidates[:max_results]:
			print(f'\t{candidate}')
		print('Try again with an exact name.')
	else:
		print('Try double checking the file `Vienna_trains.png`')


'''
Examples:

station_names = [
	"Westbahnhof", "Westbahnhof S", "Karlsplatz", "Oper, Karlsplatz", "Bahnhof", "Hauptbahnhof"
]
duplicates = detect_possible_duplicates(station_names)
print(duplicates)

or

form TransitGraph import TransitGraph as TG
net = TG()
for pair in detect_possible_duplicates(list(net.nodes)):
	print(pair)
'''