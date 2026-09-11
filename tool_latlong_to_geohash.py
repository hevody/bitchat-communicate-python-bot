import pygeohash
import json

# print(pygeohash.decode("wd"))
# print(pygeohash.encode(
# 	latitude=14.0625,
# 	longitude=118.125
# 						))

def convert_to_geohash(latlong: list):
	print(pygeohash.encode(
		latitude=latlong[0],
		longitude=latlong[1]
		))
	input()

if __name__ == '__main__':
	with open('regions.json') as f:
		regions = json.load(fp=f)

PH_REGIONS = regions["PH_REGIONS"]

for region in PH_REGIONS:
	print(region)
	# print(PH_REGIONS[region][0][0]) # this is lat
	# print(PH_REGIONS[region][0][1]) # this is long
	convert_to_geohash(PH_REGIONS[region][0])
