import csv
import pygeohash
import math

# in this part, we are going to use vectors and pythagorean theorem

def calculate_displacement(lat_relay: float, long_relay: float, lat_geohash: float, long_geohash: float) -> float:

    displacement = math.sqrt(((lat_relay - lat_geohash)**2) + ((long_relay - long_geohash)**2))
    return displacement

def find_closest_relay(geohash: str) -> list:
    relay_proximity = {}

    lat_geohash, long_geohash = pygeohash.decode(geohash=geohash)

    with open('nostr_relays.csv', mode='r', newline='', encoding='utf-8') as file:
        dict_reader = csv.DictReader(file)
        for relay in dict_reader:
            calculated_displacement = calculate_displacement(
                    lat_relay=float(relay["Latitude"]),
                    long_relay=float(relay["Longitude"]),
                    lat_geohash=lat_geohash,
                    long_geohash=long_geohash
                )

            relay_proximity[f'wss://{relay["Relay URL"]}'] = calculated_displacement

    relay_proximity_sorted = dict(sorted(relay_proximity.items(), key=lambda item: item[1]))
    print(list(relay_proximity_sorted))

if __name__ == '__main__':
    close_relays_list = find_closest_relay(geohash="wd")