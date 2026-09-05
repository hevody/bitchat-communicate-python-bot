import json
from dotenv import load_dotenv
import os

load_dotenv()
CONFIG_FILE = './config.json'


with open(CONFIG_FILE) as f:
	settings = json.load(fp=f)

PRIVATE_KEY = os.getenv("PRIVATE_KEY")



def scan_vicinity():
	pass

def main():
	pass

if __name__ == '__main__':
	main()
