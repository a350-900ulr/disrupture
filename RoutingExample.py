origin = 'Radetzkplatz'
target = 'Schloss Schönbrunn'


from TransitGraph import TransitGraph as TG
net = TG()
net.print_fastest_path(origin, target)
