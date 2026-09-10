import csv
import pygeohash
import math


# # Method B: Read as Dictionaries (Recommended for mapped column names)
# with open('nostr_relays.csv', mode='r', newline='', encoding='utf-8') as file:
#     dict_reader = csv.DictReader(file)
#     print(dict_reader)
#     for row in dict_reader:
#         print(row)
#     #     print(row['Latitude'], row['Longitude'])  # Access values by column header

# in this part, we are going to use vectors and pythagorean theorem

def calculate_displacement(lat_relay: float, long_relay: float, lat_geohash: float, long_geohash: float) -> float:

    displacement = math.sqrt(((lat_relay - lat_geohash)**2) + ((long_relay - long_geohash)**2))
    return displacement

if __name__ == '__main__':
    relay_proximity = {}

    lat_geohash, long_geohash = pygeohash.decode(geohash="wd")

    with open('nostr_relays.csv', mode='r', newline='', encoding='utf-8') as file:
        dict_reader = csv.DictReader(file)
        for relay in dict_reader:
            # print(relay['Latitude'], relay['Longitude'])  

            calculated_displacement = calculate_displacement(
                    lat_relay=float(relay["Latitude"]),
                    long_relay=float(relay["Longitude"]),
                    lat_geohash=lat_geohash,
                    long_geohash=long_geohash
                )

            relay_proximity[relay["Relay URL"]] = calculated_displacement
            print(f'{relay["Relay URL"]}: {calculated_displacement} away')

    print(relay_proximity)