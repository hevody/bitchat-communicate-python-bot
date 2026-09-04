import hashlib
import json


pubkey = 'bd1a6d06654d69939336a75b2a68ac1abf060884d5cbe13bf6bd2f25dae8a214'
created_at = 1788482388 
kind = 20000
tags = [['g', 'wd'], ['n', 'glazer'], ['nonce', '69489', '12']]
content = 'glazer po itu'

serialization_list_for_id = [0,
						pubkey,
						created_at,
						kind,
						tags,
						content]



serialized = json.dumps(
	serialization_list_for_id,
	separators=(',', ':')
	)

event_id = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
print(event_id)
print(serialized)


def main():
	pass

if __name__ == '__main__':
	main()

