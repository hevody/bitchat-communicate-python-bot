import send.send_message_nostr as sender
import random
import json

from main import Sender, TestData
from dotenv import load_dotenv
import os

with open('config.json') as f:
	config = json.load(fp=f)
with open('regions.json') as f:
	regions = json.load(fp=f)

load_dotenv()

if __name__ == '__main__':
	PRIVATE_KEY = os.getenv("STATIC_PRIVATE_KEY")
	sender = Sender()
	test_data = TestData()
	PH_REGIONS = regions["PH_REGIONS"]

	for region in PH_REGIONS:

		tags = test_data.tags
		tags[0] = ["g", PH_REGIONS[region][1]]
		publish_output = sender.send(
			test_data.GEOHASH_CHANNEL_KIND,
			tags,
			test_data.content,
			["wss://nostr-01.yakihonne.com"])
		print(publish_output)

	