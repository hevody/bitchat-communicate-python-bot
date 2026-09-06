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

def scan_vicinity():
	fetched_data = read_api.main()
	for fetched_datum in fetched_data:
		print([fetched_datum["geohash"], fetched_datum["username"]]) 

def main():

	# response = sender.send(	PRIVATE_KEY=PRIVATE_KEY,
	# 						kind=20000,
	# 						tags=tags,
	# 						content=message,
	# 						proof_of_work=enable_proof_of_work, 
	# 						relays=relays)
	# print(response)

	scan_vicinity()





if __name__ == '__main__':
	main()
