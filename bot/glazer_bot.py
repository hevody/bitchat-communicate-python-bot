import json
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import send.send_message_nostr as sender
import read.bitchatexplorer_api as read_api

load_dotenv()
CONFIG_FILE = './config.json'

with open(CONFIG_FILE) as f:
	config = json.load(fp=f)

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
tags = config["BOT_CONFIG"]["tags"]
message = "wassup pipinos"
enable_proof_of_work = config["enable_proof_of_work"]
relays = config["RELAYS"]
PH_GEOHASHES = config["BOT_CONFIG"]["PHILIPPINE_GEOHASHES"]

def scan_vicinity(fetched_data) -> list:
	
	ph_geohash_with_users = {}
	for fetched_datum in fetched_data:
		for PH_GEOHASH_INITIALS in PH_GEOHASHES:

			if fetched_datum["geohash"] == 'wd':
				continue

			if fetched_datum["geohash"].startswith(PH_GEOHASH_INITIALS):
				ph_geohash_with_users[fetched_datum["geohash"]] = ph_geohash_with_users.get(fetched_datum["geohash"], []) + [fetched_datum["username"]]

	print(ph_geohash_with_users)
				
def main():

	# response = sender.send(	PRIVATE_KEY=PRIVATE_KEY,
	# 						kind=20000,
	# 						tags=tags,
	# 						content=message,
	# 						proof_of_work=enable_proof_of_work, 
	# 						relays=relays)
	# print(response)

	
	fetched_data_from_api = read_api.main()
	active_geohashes_ph = scan_vicinity(fetched_data_from_api)




if __name__ == '__main__':
	main()
