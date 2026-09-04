import hashlib
import json
import time

SETTINGS_JSON_PATH = './settings.json'

with open(SETTINGS_JSON_PATH) as f:
	settings = json.load(fp=f)

nonce_difficulty = int(settings["nonce_difficulty"])

def mine_a_nonce(pubkey: str, kind: int, tags: list, content: str) -> tuple[int, list, str]:
	nonce_list = ['nonce', '', str(nonce_difficulty)]		# this is to be appended to tags[-1]
	tags.append([])

	nonce_found = False
	mined_nonce = 0

	while not nonce_found:
		nonce_list[1] = str(mined_nonce)
		tags[-1] = nonce_list
		created_at = int(time.time())

		serialization_list_for_id = [	0,
										pubkey,
										created_at,
										kind,
										tags,
										content
									]

		serialized = json.dumps(
		serialization_list_for_id,
		separators=(',', ':'),
		ensure_ascii=False
		)		

		event_id_bytes = hashlib.sha256(serialized.encode('utf-8')).digest()
		event_id_bits = bin(int.from_bytes(event_id_bytes, byteorder='big'))[2:].zfill(256)		

		if event_id_bits[:nonce_difficulty] == '0'*nonce_difficulty:
			nonce_found = True
		else:
			mined_nonce += 1	
			nonce_found = False

	event_id = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

	return created_at, tags, event_id