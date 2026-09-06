import send.send_message_nostr as sender
import random
import json

with open('config.json') as f:
	config = json.load(fp=f)

chars = config["BOT_CONFIG"]["GEOHASHES_ACCEPTED_LETTERS_AND_NUMBERS"]
PH_GEOHASHES = config["BOT_CONFIG"]["PHILIPPINE_GEOHASHES"]


if __name__ == '__main__':
	tags = config["TESTS"]["tags"]
	relays, enable_proof_of_work, PRIVATE_KEY = sender.load_necessary_data()

	for _ in range(10):
		ph_geohash = random.choice(PH_GEOHASHES)
		random_geohash = ph_geohash + "".join(random.choices(chars, k=3))
		
		tags[0] = ["g", random_geohash]
		message = "have a look around"

		response = sender.send(PRIVATE_KEY=PRIVATE_KEY,
						kind=20000,
						tags=tags,
						content=message,
						proof_of_work=enable_proof_of_work, 
						relays=relays)

		if response[2] != False:
			print("[+] Message was sent successfully, erp...!") 
		else:
			print(response)
	