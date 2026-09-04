import json
import time
import hashlib
import websockets
from coincurve import PrivateKey
from dotenv import load_dotenv
import os
import websocket 

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
pk_SIGNER = PrivateKey(bytes.fromhex(PRIVATE_KEY))
PUBLIC_KEY = pk_SIGNER.public_key_xonly.format().hex()

content = ""
created_at = int(time.time())
kind = 20000
tags = [['g', 'wd'], ['n', 'glazer']]

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


PrivateKey().sign_schnorr(bytes.fromhex(event_id)).hex()
signature = pk_SIGNER.sign_schnorr(bytes.fromhex(event_id)).hex()

event = {
	"id": event_id,
	"pubkey": PUBLIC_KEY,
	"created_at": created_at,
	"kind": kind,
	"tags": tags,
	"content": content,
	"sig": signature
}

ws = websocket.create_connection("wss://nos.lol")
ws.send(json.dumps(["EVENT", event]))
response = ws.recv()
print(f"Response {response}")
ws.close()

