import main
import time

GEOHASH_REPLY_LIMIT = 25

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
	for geohash in vicinity_geohashes:
		tagged_names = [f"@{username}" for username in vicinity_geohashes[geohash]]

		tagged_names = list(set(tagged_names))

		# humanizing the messages
		if len(tagged_names) == 1:
			mention_in_message = tagged_names[0]
		if len(tagged_names) == 2:
			mention_in_message = " and ".join(tagged_names)
		if len(tagged_names) > 2:
			mention_in_message = ", ".join(tagged_names[:-1]) + ", and " + tagged_names[-1]
		
		message = f"Hi, {mention_in_message}!"

		tags[0] = ["g", geohash]
		response = main.Sender().send(	
						kind=GEOHASH_KIND,
						tags=tags,
						content=message,
						relays=main.ProximityRelay().find_closest_relay(geohash))
		print(response)
 
if __name__ == '__main__':
	config = main.Config()
	bot = main.Bot()

	HEADERS = config.GENERAL_HEADERS
	BC_EXPLORER_API = config.BITCHAT_EXPLORER_API
	GEOHASH_KIND = bot.GEOHASH_CHANNEL_KIND
	tags = bot.tags


	PH_GEOHASHES = ["we", "wg", "wd", "wf", "w9", "wc", "w8", "wb"]
	BLOCKED_USERNAMES = ["not_glazer", "lazer🇵🇭 Bot"]

	while True:
		fetched_data = main.Reader().perform_get_request(BC_EXPLORER_API, HEADERS)
		geohash_and_its_users = scan_vicinity(fetched_data)
		send_vicinity(geohash_and_its_users)

		time.sleep(1 * 60)