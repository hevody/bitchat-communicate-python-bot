from coincurve import PrivateKey
import secrets
import hmac
from dotenv import load_dotenv
import json
import os
import hashlib

with open('config.json') as f:
	config = json.load(fp=f)

load_dotenv()

# PRIVATE_KEY_FUNCTION_CALL = PrivateKey()
# PRIVATE_KEY = PRIVATE_KEY_FUNCTION_CALL.secret.hex()
# PUBLIC_KEY = PRIVATE_KEY_FUNCTION_CALL.public_key_xonly.format().hex()



# print(f"Private key: {PRIVATE_KEY}")
# print(f"Public key:  {PUBLIC_KEY}")

def derive_geohash_private_key(seed: bytes, geohash: str):
	pass	

	private_key = hmac.new(
		seed, 
		geohash.encode("utf-8"),
		hashlib.sha256,
	).digest()

	# input(private_key)

	while True:
		try:
			PrivateKey(private_key)
			return private_key
		except ValueError:
			private_key = hmac.new(
				seed, 
				private_key,
				hashlib.sha256,
			).digest()			

def generate_seed():
	print('[*] Generating a seed...')
	seed = secrets.token_bytes(32)
	print(seed.hex())

	env_seed_content = f'SEED="{seed.hex()}"'
	with open('.env', 'w') as f:
		f.write(env_seed_content)
	print('[*] Seed wrote to .env file successfully!\n')

if __name__ == '__main__':
	#generate_seed()
	
	geohash = 'wd'
	SEED = bytes.fromhex(os.getenv("SEED"))
	geohash_specific_private_key = derive_geohash_private_key(	seed=SEED,
																geohash=geohash)
	print(geohash_specific_private_key.hex())