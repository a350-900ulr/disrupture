from difflib import SequenceMatcher
from TransitGraph import TransitGraph as TG


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


# station_names = ["Westbahnhof", "Westbahnhof S", "Karlsplatz", "Oper, Karlsplatz", "Bahnhof", "Hauptbahnhof"]
# duplicates = detect_possible_duplicates(station_names)
# print(duplicates)

net = TG()

for pair in detect_possible_duplicates(list(net.nodes)):
	print(pair)

