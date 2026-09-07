from dotenv import load_dotenv
import json
import os

def load_necessary_data() -> tuple[list, bool, str]:
	load_dotenv()
	with open("config.json") as f:
		config = json.load(fp=f)
	
	relays = config["RELAYS"]
	enable_proof_of_work = config["enable_proof_of_work"]
	PRIVATE_KEY = os.getenv("PRIVATE_KEY")

	return relays, enable_proof_of_work, PRIVATE_KEY