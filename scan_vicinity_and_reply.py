import main
import time
from datetime import datetime
from flask import Flask
import os

app = Flask(__name__)
config = main.Config()
bot = main.Bot()

GEOHASH_REPLY_LIMIT = 35
PORT = int(os.environ.get("PORT", 7860))
PH_GEOHASHES = ["we", "wg", "wd", "wf", "w9", "wc", "w8", "wb"]
BLOCKED_USERNAMES = ["lazer🇵🇭 Bot"]

def scan_vicinity(fetched_data) -> dict[list]:
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

def send_vicinity(vicinity_geohashes: dict):
	tags = bot.tags
	GEOHASH_KIND = bot.GEOHASH_CHANNEL_KIND

	for geohash in vicinity_geohashes:
		if geohash in replied_geohash:
			continue
		tagged_names = [f"@{username}" for username in vicinity_geohashes[geohash]]

		tagged_names = list(set(tagged_names))

		# humanizing the messages
		if len(tagged_names) == 1:
			mention_in_message = tagged_names[0]
		if len(tagged_names) == 2:
			mention_in_message = " at ".join(tagged_names)
		if len(tagged_names) > 2:
			mention_in_message = ", ".join(tagged_names[:-1]) + ", at " + tagged_names[-1]
		
		message = f"Kumusta, {mention_in_message}!"

		tags[0] = ["g", geohash]
		response = main.Sender().send(	
						kind=GEOHASH_KIND,
						tags=tags,
						content=message,
						relays=main.ProximityRelay().find_closest_relay(geohash))
		print(response)

def detect_abuse():
	pass
 
def detect_and_reply():
	print('[*] Program ran')
	HEADERS = config.GENERAL_HEADERS
	BC_EXPLORER_API = config.BITCHAT_EXPLORER_API
	
		
	global replied_geohash
	replied_geohash = []
	while True:
		now = datetime.now()
		if now.strftime("%M") == "8" or now.strftime("%M") == "38":		# breaks at minute 8 and 38, wait for cron ping to run again
			break
		if len(replied_geohash) > GEOHASH_REPLY_LIMIT:
			break
		


		fetched_data = main.Reader().perform_get_request(BC_EXPLORER_API, HEADERS)
		geohash_and_its_users = scan_vicinity(fetched_data)
		send_vicinity(geohash_and_its_users)
		
		unique_geohash_reply = list(set(list(geohash_and_its_users)) - set(replied_geohash))


		replied_geohash += unique_geohash_reply

		
		print("[*] Sleeping for 60 seconds")
		time.sleep(1* 60)

	print('[*] Prog breaks out the while loop')

@app.route("/")
def home():
	detect_and_reply()
	return "Wassup, bitchat"


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=PORT)