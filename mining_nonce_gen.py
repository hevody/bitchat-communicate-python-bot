import hashlib
import json

# return: created_at, nonce_list, id  
# interested: mined_nonce





with open('settings.json') as f:
	settings = json.load(fp=f)

nonce_difficulty = int(settings["nonce_difficulty"])













def main(pubkey: str, kind: int, tags: list, content: str) -> tuple[str]:
	nonce_list = ['nonce', '', str(nonce_difficulty)]		# this is to be appended to tags[-1]
	tags.append([])

	# for testing purposes:
	# there will be a value for created_at
	created_at = 1788482388 

	nonce_found = False
	mined_nonce = 69489

	while not nonce_found:
		nonce_list[1] = str(mined_nonce)
		tags[-1] = nonce_list

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

		#print(serialized)

		event_id_bytes = hashlib.sha256(serialized.encode('utf-8')).digest()
		event_id_bits = bin(int.from_bytes(event_id_bytes, byteorder='big'))[2:].zfill(256)		

		if event_id_bits[:nonce_difficulty] == '0'*nonce_difficulty:
			nonce_found = True
		else:
			mined_nonce += 1	
			nonce_found = False

	print(mined_nonce)
	event_id = hashlib.sha256(serialized.encode('utf-8')).hexdigest()


	return created_at, tags, event_id


		



	
	


	

	


	






pubkey = 'bd1a6d06654d69939336a75b2a68ac1abf060884d5cbe13bf6bd2f25dae8a214'
created_at = 1788482388 
kind = 20000
tags = [['g', 'wd'], ['n', 'glazer']]
content = 'glazer po itu'

if __name__ == '__main__':
	get_mined_data = main(	pubkey=pubkey, 
							kind=kind, 
							tags=tags, 
							content=content
						)
	print(get_mined_data)



