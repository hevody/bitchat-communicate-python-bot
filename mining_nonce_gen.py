import hashlib
import json


pubkey = 'bd1a6d06654d69939336a75b2a68ac1abf060884d5cbe13bf6bd2f25dae8a214'
created_at = 1788482388 
kind = 20000
tags = [['g', 'wd'], ['n', 'glazer']]
content = 'glazer po itu'


with open('settings.json') as f:
	settings = json.load(fp=f)

nonce_difficulty = settings["nonce_difficulty"]

mined_nonce = 100

nonce_list = ['nonce', f'{mined_nonce}', f'{nonce_difficulty}']

input(nonce_list)


serialization_list_for_id = [0,
						pubkey,
						created_at,
						kind,
						tags,
						content]

serialized = json.dumps(
	serialization_list_for_id,
	separators=(',', ':'),
	ensure_ascii=False
	)

# event_id = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

event_id_bytes = hashlib.sha256(serialized.encode('utf-8')).digest()
event_id_bits = bin(int.from_bytes(event_id_bytes, byteorder='big'))[2:].zfill(256)



print(event_id_bits)
print(serialized)


def main():
	pass

if __name__ == '__main__':
	main()

