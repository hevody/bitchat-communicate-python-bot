import json
import time
from dotenv import load_dotenv
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import art.art_resource as art
import send.send_message_nostr as sender

if __name__ == '__main__':

	load_dotenv()
	with open("config.json") as f:
		config = json.load(fp=f)
	
	# relays = config["RELAYS"]
	relays = ["wss://relay01.lnfi.network:443"]
	enable_proof_of_work = config["enable_proof_of_work"]
	PRIVATE_KEY = os.getenv("PRIVATE_KEY")


	print(art.ascii_art_temple())
	print(art.ascii_art_text())

	tags = config["pre-made_event_for_weapons"]["tags"]
	content = config["pre-made_event_for_weapons"]["content"]

	while True:
		response = sender.send(PRIVATE_KEY=PRIVATE_KEY,
					kind=20000,
					tags=tags,
					content=content,
					proof_of_work=enable_proof_of_work, 
					relays=relays)




















