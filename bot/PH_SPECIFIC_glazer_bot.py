import json
from dotenv import load_dotenv
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import send.send_message_nostr as sender
import read.bitchatexplorer_api as read_api
import main

load_dotenv()
CONFIG_FILE = './config.json'

with open(CONFIG_FILE) as f:
	config = json.load(fp=f)

tags = config["BOT_CONFIG"]["PH"]["tags"]
message = "wassup pipinos"
PH_GEOHASHES = config["BOT_CONFIG"]["PH"]["PHILIPPINE_GEOHASHES"]
BLOCKED_USERNAMES = config["BOT_CONFIG"]["BLOCKED_USERNAMES"]
BLOCKED_GEOHASHES = config["BOT_CONFIG"]["BLOCKED_GEOHASHES"]
CATEGORY_DATABASE = config["BOT_CONFIG"]["CATEGORY_DATABASE"]

def scan_vicinity(fetched_data) -> list:
	
	ph_geohash_with_users = {}
	for fetched_datum in fetched_data:
		for PH_GEOHASH_INITIALS in PH_GEOHASHES:

			if fetched_datum["geohash"] == 'wd':
				continue

			if fetched_datum["geohash"].startswith(PH_GEOHASH_INITIALS):
				if fetched_datum["username"] in BLOCKED_USERNAMES:
					continue
				ph_geohash_with_users[fetched_datum["geohash"]] = ph_geohash_with_users.get(fetched_datum["geohash"], []) + [fetched_datum["username"]]

	return ph_geohash_with_users

def send_vicinity(vicinity_geohashes: dict, relays, enable_proof_of_work, PRIVATE_KEY):
	for geohash in vicinity_geohashes:
		tagged_names = [f"@{username}" for username in vicinity_geohashes[geohash]]

		tagged_names = list(set(tagged_names))

		if len(tagged_names) == 1:
			mention_in_message = tagged_names[0]
		if len(tagged_names) == 2:
			mention_in_message = " and ".join(tagged_names)
		
		if len(tagged_names) > 2:
			mention_in_message = ", ".join(tagged_names[:-1]) + ", and " + tagged_names[-1]
		message = f"Hi, {mention_in_message}!"

		tags[0] = ["g", geohash]
		response = sender.send(	PRIVATE_KEY=PRIVATE_KEY,
						kind=20000,
						tags=tags,
						content=message,
						proof_of_work=enable_proof_of_work, 
						relays=relays)

def frequency_geohash(fetched_data):
	geohash_with_frequency= {}
	for fetched_datum in fetched_data:
		if fetched_datum["geohash"] in BLOCKED_GEOHASHES:
			continue
		geohash_with_frequency[fetched_datum["channel"]] = geohash_with_frequency.get(fetched_datum["channel"], 0) + 1

	descending_geohash_with_frequency = dict(sorted(geohash_with_frequency.items(), key=lambda item: item[1], reverse=True))

	return descending_geohash_with_frequency

def content_builder(geohash_with_frequency):
	heading_geohash_frequency = "\nBisitahin niyo rin ang mga geohashes na ito:\n"
	body_geohash_frequency = ""

	five = 0
	for geohash in geohash_with_frequency:
		if five == 5:
			break
		if geohash in CATEGORY_DATABASE:
			category_value_of_geohash = CATEGORY_DATABASE[geohash]
			geohash_and_category = f"{geohash} ({category_value_of_geohash})"
			body_geohash_frequency += f"{geohash_and_category.ljust(15)}: {geohash_with_frequency[geohash]} chats\n"
		else:
			body_geohash_frequency += f"{geohash.ljust(15)}: {geohash_with_frequency[geohash]} chats\n"
		five += 1
	geohash_frequency_message = heading_geohash_frequency + body_geohash_frequency
	return geohash_frequency_message

def news_rss_reader():
	pass

def main_bot():
	relays, enable_proof_of_work, PRIVATE_KEY = main.load_necessary_data()	
	# response = sender.send(	PRIVATE_KEY=PRIVATE_KEY,
	# 						kind=20000,
	# 						tags=tags,
	# 						content=message,
	# 						proof_of_work=enable_proof_of_work, 
	# 						relays=relays)
	# print(response)

	fetched_data_from_api = read_api.main()

	active_geohashes_ph = scan_vicinity(fetched_data_from_api)
	relays = ["wss://nostr-01.yakihonne.com"]
	send_vicinity(active_geohashes_ph, relays, enable_proof_of_work, PRIVATE_KEY)

	frequent_geohash = frequency_geohash(fetched_data_from_api)

	message = content_builder(frequent_geohash)
	

	tags[0] = ["g", "wd"]
	response = sender.send(	PRIVATE_KEY=PRIVATE_KEY,
						kind=20000,
						tags=tags,
						content=message,
						proof_of_work=enable_proof_of_work, 
						relays=relays)



if __name__ == '__main__':
	main_bot()
