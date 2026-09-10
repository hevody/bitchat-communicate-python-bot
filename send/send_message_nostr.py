import json
import time
import hashlib
import websockets
from coincurve import PrivateKey
import os
import websocket 
import logging
import time

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cryptography_specific.mining_nonce_gen as mine_pow
import art.art_resource as art
import main

def event_generator(PRIVATE_KEY: str, kind: int, tags: list, content: str, proof_of_work: bool):
	pk_SIGNER = PrivateKey(bytes.fromhex(PRIVATE_KEY))
	PUBLIC_KEY = pk_SIGNER.public_key_xonly.format().hex()

	if proof_of_work: 
		created_at, tags, event_id = mine_pow.mine_a_nonce(	pubkey=PUBLIC_KEY, 
															kind=kind,
															tags=tags,
															content=content
														)

	else:
		created_at = int(time.time())

		serialization_list_for_id = [0,
							PUBLIC_KEY,
							created_at,
							kind,
							tags,
							content]

		serialized = json.dumps(
		serialization_list_for_id,
		separators=(',', ':'),
		ensure_ascii=False
		)

		event_id = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

	signature = pk_SIGNER.sign_schnorr(bytes.fromhex(event_id)).hex()

	event = {
		"content": content,
		"created_at": created_at,
		"id": event_id,
		"kind": kind,
		"pubkey": PUBLIC_KEY,
		"sig": signature,
		"tags": tags,
	}

	return event

def send_event_to_relay(event: dict, relays: list) -> list:
	for relay in relays:
		try:
			ws = websocket.create_connection(relay)
			# ws.send(json.dumps(["EVENT", event]))
			ws.send(json.dumps(["EVENT", event]))
			response = ws.recv()
			print(response)

			if json.loads(response)[0] != "OK":
				ws.close()
				continue
			else:
				ws.close()
				return json.loads(response)
		except KeyboardInterrupt:
			exit()
		except Exception as e: 
			return e
			continue

def send(PRIVATE_KEY: str, kind: int, tags: list, content: str, proof_of_work: bool, relays: list):

	event_created = event_generator(PRIVATE_KEY=PRIVATE_KEY,
									kind=kind,
									tags=tags,
									content=content,
									proof_of_work=proof_of_work,
									)
	print(event_created)

	outbound_send_result = send_event_to_relay(event=event_created,
										relays=relays)

	return outbound_send_result

if __name__ == '__main__':

	relays, enable_proof_of_work, PRIVATE_KEY = main.load_necessary_data()

	print(art.ascii_art_temple())
	print(art.ascii_art_text())

	tags = []
	PADDING = 10
	geohash = input("geohash".ljust(PADDING) + '> ')
	tags.append(["g", geohash])
	username = input("username".ljust(PADDING) + '> ')
	tags.append(["n", username])
	message = input("send".ljust(PADDING) + '> ')


	# with open('config.json') as f:
	# 	config = json.load(fp=f)
	# relays = config["RELAYS"]

	# ### showing presence ###
	relays = ["wss://relay01.lnfi.network:443"]
	# while True:
	# 	show_presence = send(PRIVATE_KEY=PRIVATE_KEY,
	# 					kind=20001,
	# 					# tags=[tags[0]],
	# 					tags=tags[:2],
	# 					content="",
	# 					proof_of_work=False, 
	# 					relays=relays)

	
	show_presence = send(PRIVATE_KEY=PRIVATE_KEY,
						kind=20001,
						tags=[tags[0]],
						content="",
						proof_of_work=False, 
						relays=relays)
	
	time.sleep(5)
	response = send(PRIVATE_KEY=PRIVATE_KEY,
					kind=20000,
					tags=tags,
					content=message,
					proof_of_work=enable_proof_of_work, 
					relays=relays)

	print(response)
	if response[2] != False:
		print("[+] Message was sent successfully, erp...!") 
	else:
		print(response)

















