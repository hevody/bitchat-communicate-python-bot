import hmac
import hashlib
import struct
from coincurve import PrivateKey

from dotenv import load_dotenv
import os

import json
import time
import secrets
import websocket

import threading

load_dotenv()

RELAY_URL = "wss://relay01.lnfi.network:443"


def candidate_key(seed: bytes, geohash: str, iteration: int) -> bytes:
	msg = geohash.encode("utf-8") + struct.pack(">I", iteration)
	return hmac.new(seed,
					msg,
					hashlib.sha256).digest()

def derive_identity(seed: bytes, geohash: str):
	for i in range(10):
		print(i)
		key_bytes = candidate_key(	seed,
									geohash,
									i
								)
		try:
			return PrivateKey(key_bytes)
		except ValueError:
			continue
	fallback = hashlib.sha256(seed + geohash.encode("utf-8").digest())
	return PrivateKey(fallback)

def generate_keypair(priv_identity: bytes):
	pub_xonly = priv_identity.public_key.format(compressed=True)[1:]
	return pub_xonly.hex()

def event_id(pubkey_hex, created_at, kind, tags, content):
	serialized = json.dumps(
		[0,
		pubkey_hex,
		created_at,
		kind,
		tags,
		content
		],
		separators=(",", ":"), ensure_ascii=False
	)
	return hashlib.sha256(serialized.encode()).hexdigest()

def sign_event(priv: PrivateKey, pubkey_hex, kind, tags, content):
	created_at = int(time.time())
	eid = event_id(pubkey_hex, created_at, kind, tags, content)
	sig = priv.sign_schnorr(bytes.fromhex(eid))
	return {
		"id": eid,
		"pubkey": pubkey_hex,
		"created_at": created_at,
		"kind": kind,
		"tags": tags,
		"content": content,
		"sig": sig.hex(),
	}

def publish(event):
	ws = websocket.create_connection(RELAY_URL)
	ws.send(json.dumps(["EVENT", event]))
	print(ws.recv())
	ws.close()


def create_ephemeral_geohash_event(priv, pubkey_hex, geohash, content, nickname=None, teleported=True):
	tags = [["g", geohash]]
	if teleported:
		tags.append(["t", "teleport"])
	if nickname:
		tags.append(["n", nickname])
	return sign_event(priv, pubkey_hex, 20000, tags, content)

def create_geohash_presence_event(priv, pubkey_hex, geohash):
	return sign_event(priv, pubkey_hex, 20001, [["g", geohash]], "")

def presence_loop(identity, pubkey_hex, GEOHASH):
	for _ in range(25):
		print(_)
		presence_event = create_geohash_presence_event(identity, pubkey_hex, GEOHASH)
		publish(presence_event)
		time.sleep(2)

if __name__ == '__main__':
	GEOHASH = 'wdw'
	SEED = bytes.fromhex(os.getenv("SEED"))
	

	identity = derive_identity(	seed=SEED, 
								geohash=GEOHASH
							)

	print('private key:')
	print(identity.secret.hex())

	print("public key:")
	pubkey_hex = generate_keypair(priv_identity=identity)
	print(pubkey_hex)

	presence_thread = threading.Thread(target=presence_loop, args=(identity, pubkey_hex, GEOHASH))	
	presence_thread.start()

	chat_event = create_ephemeral_geohash_event(
		identity,
		pubkey_hex,
		GEOHASH,
		content="welcome, have a look around...",
		nickname="glazer"
	)

	time.sleep(60)
	print(chat_event)
	publish(chat_event)

	presence_thread.join()

	# presence_event = create_geohash_presence_event(identity, pubkey_hex, GEOHASH)
	# publish(presence_event)x