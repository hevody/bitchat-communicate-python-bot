import random
import json
import main
import string

LEGACY_CONFIG_PATH = './legacy/config.json'
CHARACTERS = string.ascii_letters + string.digits


with open(LEGACY_CONFIG_PATH) as f:
	config = json.load(fp=f)

chars = config["BOT_CONFIG"]["GEOHASHES_ACCEPTED_LETTERS_AND_NUMBERS"]
PH_GEOHASHES = config["BOT_CONFIG"]["PH"]["PHILIPPINE_GEOHASHES"]

if __name__ == '__main__':
	tags = config["TESTS"]["tags"]
	GEOHASH_KIND = 20000

	for _ in range(10):
		ph_geohash = random.choice(PH_GEOHASHES)
		random_geohash = ph_geohash + "".join(random.choices(chars, k=3))
		
		tags[0] = ["g", random_geohash]
		tags[2] = ["n", ''.join(random.choices(CHARACTERS, k=5))]
		message = "have a look around"

		response = main.Sender().send(	
						kind=GEOHASH_KIND,
						tags=tags,
						content=message,
						relays=main.ProximityRelay().find_closest_relay(random_geohash))

		print(response)
		if response[2] != False:
			print("[+] Message was sent successfully, erp...!") 
		else:
			print(response)
	