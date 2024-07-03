import osmium
import csv

class GasStationHandler(osmium.SimpleHandler):
    def __init__(self):
        super(GasStationHandler, self).__init__()
        self.gas_stations = []

    def node(self, n):
        if 'amenity' in n.tags and n.tags['amenity'] == 'fuel':
            self.gas_stations.append({
                'id': n.id,
                'lat': n.location.lat,
                'lon': n.location.lon,
                'name': n.tags.get('name', 'N/A')
            })

    def way(self, w):
        if 'amenity' in w.tags and w.tags['amenity'] == 'fuel':
            try:
                center = w.nodes[0]
                self.gas_stations.append({
                    'id': w.id,
                    'lat': center.lat,
                    'lon': center.lon,
                    'name': w.tags.get('name', 'N/A')
                })
            except:
                pass  # Skip if we can't get the center

# Replace with the path to your .osm.pbf file
osm_file = 'gradio/test/haiti-and-domrep-latest.osm.pbf'

h = GasStationHandler()
h.apply_file(osm_file)

# Write results to CSV
with open('gradio/sample_data/dominican_republic_gas_stations.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['id', 'lat', 'lon', 'name'])
    writer.writeheader()
    for station in h.gas_stations:
        writer.writerow(station)

print(f"Found {len(h.gas_stations)} gas stations.")