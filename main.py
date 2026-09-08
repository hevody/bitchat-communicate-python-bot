from dotenv import load_dotenv
import json
import os
import json
import logging

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import art.art_resource as art
import cryptography_specific.generate_key as keygen

def load_necessary_data() -> tuple[list, bool, str]:
	load_dotenv()
	with open("config.json") as f:
		config = json.load(fp=f)
	
	relays = config["RELAYS"]
	enable_proof_of_work = config["enable_proof_of_work"]
	PRIVATE_KEY = os.getenv("PRIVATE_KEY")

	return relays, enable_proof_of_work, PRIVATE_KEY

def menu():
	options = {
		"Generate a seed": keygen.generate_seed,
		"Exit": exit
	}

	options_with_index = list(options)

	print('')
	for index in range(len(options_with_index)):
		print(f'\t[{index + 1}] {options_with_index[index]}')

	try:
		choice = int(input('\n> ')) - 1
	except KeyboardInterrupt:
		exit()
	except:								# when decimal is given
		return							

	# input validation
	if choice < 0:
		return
	if choice + 1 > len(options_with_index):
		return

	options[options_with_index[choice]]()

if __name__ == '__main__':
	art.show_headings()
	while True:
		menu()

