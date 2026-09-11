
import json
import os
import json
import logging

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cryptography_specific.generate_key as keygen

from dotenv import (
					load_dotenv,
					find_dotenv,
					set_key)
from coincurve import PrivateKey
import time
import hashlib
import websocket
import pygeohash
import csv
import math
import requests
from datetime import datetime
import humanize
import re
from tabulate import tabulate
import textwrap

DOTENV_PATH = find_dotenv()

def load_necessary_data() -> tuple[list, bool, str]:
	load_dotenv()
	with open("config.json") as f:
		config = json.load(fp=f)
	
	relays = config["RELAYS"]
	enable_proof_of_work = config["enable_proof_of_work"]
	PRIVATE_KEY = os.getenv("STATIC_PRIVATE_KEY")

	return relays, enable_proof_of_work, PRIVATE_KEY

def menu():
	cryptography_menu = CryptographySpecific()

	options = {
		"Generate a Private Key": cryptography_menu.save_private_key,
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

class HeadingArt:
	def __init__(self):
		print(self.ascii_art_temple())
		print(self.ascii_art_text())

	def ascii_art_temple(self):
		CYAN_ANSI_COLOR_CODE = "\033[0;36m"
		ANSI_RESET = "\033[0m"
		ASCII_ART = r'''

  	               )\         O_._._._A_._._._O         /(
                  \`--.___,'=================`.___,--'/
                   \`--._.__                 __._,--'/
                     \  ,. l`~~~~~~~~~~~~~~~'l ,.  /
         __            \||(_)!_!_!_.-._!_!_!(_)||/            __
         \\`-.__        ||_|____!!_|;|_!!____|_||        __,-'//
          \\    `==---='-----------'='-----------`=---=='    //
          | `--.                                         ,--' |
           \  ,.`~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',.  /
             \||  ____,-------._,-------._,-------.____  ||/
              ||\|___!`======="!`======="!`======="!___|/||
              || |---||--------||-| | |-!!--------||---| ||
    __O_____O_ll_lO_____O_____O|| |'|'| ||O_____O_____Ol_ll_O_____O__
    o H o o H o o H o o H o o |-----------| o o H o o H o o H o o H o
   ___H_____H_____H_____H____O =========== O____H_____H_____H_____H___
                            /|=============|\
  ()______()______()______() '==== +-+ ====' ()______()______()______()
  ||{_}{_}||{_}{_}||{_}{_}/| ===== |_| ===== |\{_}{_}||{_}{_}||{_}{_}||
  ||      ||      ||     / |==== s(   )s ====| \     ||      ||      ||
  ======================()  =================  ()======================
  ----------------------/| ------------------- |\----------------------
                       / |---------------------| \
  -'--'--'           ()  '---------------------'  ()
                     /| ------------------------- |\    --'--'--'
         --'--'     / |---------------------------| \    '--'
                  ()  |___________________________|  ()           '--'-
    --'-          /| _______________________________  |\
   --'           / |__________________________________| \

		'''
		return CYAN_ANSI_COLOR_CODE + ASCII_ART + ANSI_RESET

	def ascii_art_text(self):
		BOLD_ANSI = "\033[1m"
		ANSI_RESET= "\033[0m"
		USAP_NOSTR_CLIENT = r'''
                                                                              
   ▄████  ▄▄     ▄▄▄  ▄▄▄▄▄ ▄▄▄▄▄ ▄▄▄▄    ▄█████ ▄▄    ▄▄ ▄▄▄▄▄ ▄▄  ▄▄ ▄▄▄▄▄▄ 
  ██  ▄▄▄ ██    ██▀██   ▄█▀ ██▄▄  ██▄█▄   ██     ██    ██ ██▄▄  ███▄██   ██   
   ▀███▀  ██▄▄▄ ██▀██ ▄██▄▄ ██▄▄▄ ██ ██   ▀█████ ██▄▄▄ ██ ██▄▄▄ ██ ▀██   ██   
                                                                              
    usap tayo, ano tara?
	  '''
		return BOLD_ANSI + USAP_NOSTR_CLIENT + ANSI_RESET

class CryptographySpecific:
	def __init__(self):
		config = Config()
		self.NONCE_DIFFICULTY = config.NONCE_DIFFICULTY

	def save_private_key(self):
		print("\n[*] Generating a Private Key...")
		private_key = PrivateKey().secret.hex()
		print(f"[*] Generated Private Key: {private_key}")
		set_key(DOTENV_PATH, "STATIC_PRIVATE_KEY", private_key)
		load_dotenv(DOTENV_PATH, override=True)
		print(f"[*] Private Key successfully saved in {DOTENV_PATH}")

	def retrieve_signer_and_pubkey(self, private_key) -> tuple[PrivateKey, str]:
		pk_signer = PrivateKey(bytes.fromhex(private_key))
		public_key = pk_signer.public_key_xonly.format().hex()

		return pk_signer, public_key

	def mine_nonce(self, pubkey: str, kind: int, tags: list, content: str) -> tuple[int, list, str]:
		nonce_list = ['nonce', '', str(self.NONCE_DIFFICULTY)]		# this is to be appended to tags[-1]
		
																# checks if nonce tag exists, so it wouldn't add infinite nonce in tags
		
		nonce_location = -1
		nonce_location_found = False
		for tag_index in range(len(tags)):
			if tags[tag_index][0] == 'nonce':					# theoretically, nonce was found
				nonce_location = tag_index
				nonce_location_found = True

		if not nonce_location_found:
			tags.append([])

		nonce_found = False
		mined_nonce = 0

		while not nonce_found:
			nonce_list[1] = str(mined_nonce)
			tags[nonce_location] = nonce_list
			created_at = int(time.time())

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

			event_id_bytes = hashlib.sha256(serialized.encode('utf-8')).digest()
			event_id_bits = bin(int.from_bytes(event_id_bytes, byteorder='big'))[2:].zfill(256)		

			if event_id_bits[:self.NONCE_DIFFICULTY] == '0'*self.NONCE_DIFFICULTY:
				nonce_found = True
			else:
				mined_nonce += 1	
				nonce_found = False

		event_id = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

		return created_at, tags, event_id

class Config:
	def __init__(self):
		self.DEBUG = True
		self.POW = True
		self.LOG = True
		self.USE_STATIC_PRIVATE_KEY = True
		self.NONCE_DIFFICULTY = 15
		self.RELAYS_LEGACY = ["wss://21milionidinostr.duckdns.org", "wss://offchain.bostr.online", "wss://yabu.me", "wss://nos.lol", "wss://nostr-relay.zimage.com", "wss://nostr.twinkle.lol", "wss://nostr.2b9t.xyz", "wss://bitcoinostr.duckdns.org", "wss://nostr.dlcdevkit.com", "wss://relay01.lnfi.network", "wss://bucket.coracle.social", "wss://cdn.satellite.earth", "wss://staging.yabu.me", "wss://relay.islandbitcoin.com", "wss://nostr-relay.nextblockvending.com", "wss://nostr.whitenode45.ddns.net", "wss://no.str.cr", "wss://nostr-relay.xbytez.io", "wss://relay.illuminodes.com", "wss://relay.pyramid.li", "wss://relay.nostu.be", "wss://nostrride.io", "wss://relay.dyne.org", "wss://nostr.christiansass.de", "wss://nostr.thebiglake.org", "wss://relay02.lnfi.network", "wss://nostrrelay.taylorperron.com", "wss://relay.staging.plebeian.market", "wss://relay.guggero.org", "wss://relay.ru.ac.th", "wss://relay.damus.io", "wss://nostr.relay.hedwig.sh", "wss://nostr.myshosholoza.co.za", "wss://nostr.azzamo.net", "wss://relay.sharegap.net", "wss://relay.internationalright-wing.org", "wss://nostr-relay.corb.net", "wss://ec2.f7z.io", "wss://nostr.snowbla.de", "wss://nr.yay.so", "wss://relay1.nostrchat.io", "wss://relay.earthly.city", "wss://freelay.sovbit.host", "wss://nrl.ceskar.xyz", "wss://relay.plebeian.market", "wss://bridge.tagomago.me", "wss://offchain.pub", "wss://nostrcheck.me", "wss://relay.bowlafterbowl.com", "wss://nostr-01.yakihonne.com", "wss://nostr.4rs.nl", "wss://relay.satlantis.io", "wss://relay.mccormick.cx", "wss://adre.su", "wss://relay.laantungir.net", "wss://nostr.novacisko.cz", "wss://relay.nostrhub.fr", "wss://relay.nearhood.co.uk", "wss://nostr.unkn0wn.world", "wss://nostr.middling.mydns.jp", "wss://dev-relay.nostreon.com", "wss://myvoiceourstory.org", "wss://nostr.islandarea.net"]
		self.GENERAL_HEADERS = {
    "User-Agent": "Mozlla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Connection": "keep-alive"
  	}
		self.BITCHAT_EXPLORER_API = "https://bitchatexplorer.com/api/messages?limit=1000"

class Sender:
	def __init__(self):
		self.cryptography = CryptographySpecific()
		config = Config()
		self.POW = config.POW

		if config.USE_STATIC_PRIVATE_KEY:
			self.pk_signer, self.public_key = self.cryptography.retrieve_signer_and_pubkey(PRIVATE_KEY)

	def event_generator(self, kind: int, tags: list, content: str):
		if self.POW: 
			created_at, tags, event_id = self.cryptography.mine_nonce(	pubkey=self.public_key, 
																	kind=kind,
																	tags=tags,
																	content=content
																)

		else:
			created_at = int(time.time())

			serialization_list_for_id = [0,
								self.public_key,
								created_at,
								kind,
								tags,
								content]

			serialized = json.dumps(
			serialization_list_for_id,
			separators=(',', ':'),
			ensure_ascii=False
			)

			event_id = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

		signature = self.pk_signer.sign_schnorr(bytes.fromhex(event_id)).hex()

		event = {
			"content": content,
			"created_at": created_at,
			"id": event_id,
			"kind": kind,
			"pubkey": self.public_key,
			"sig": signature,
			"tags": tags,
		}

		return event

	def send_event_to_relay(self, event: dict, relays: list) -> list:
		for relay in relays:
			try:
				ws = websocket.create_connection(relay)
				ws.send(json.dumps(["EVENT", event]))
				response = ws.recv()
				if json.loads(response)[0] != "OK":
					ws.close()
					continue
				else:
					ws.close()
					return json.loads(response)
			except KeyboardInterrupt:
				exit()
			except Exception as e: 
				return e
				continue

	def send(self, kind: int, tags: list, content: str, relays: list):

		event_created = self.event_generator(
										kind=kind,
										tags=tags,
										content=content
										)

		published_result = self.send_event_to_relay(
												event=event_created,
												relays=relays
												)
	
		return published_result

class ProximityRelay:
	def __init__(self):
		pass

	def calculate_displacement(self, lat_relay: float, long_relay: float, lat_geohash: float, long_geohash: float) -> float:

	    displacement = math.sqrt(((lat_relay - lat_geohash)**2) + ((long_relay - long_geohash)**2))
	    return displacement

	def find_closest_relay(self, geohash: str) -> list:
	    relay_proximity = {}

	    lat_geohash, long_geohash = pygeohash.decode(geohash=geohash)

	    with open('nostr_relays.csv', mode='r', newline='', encoding='utf-8') as file:
	        dict_reader = csv.DictReader(file)
	        for relay in dict_reader:
	            calculated_displacement = self.calculate_displacement(
	                    lat_relay=float(relay["Latitude"]),
	                    long_relay=float(relay["Longitude"]),
	                    lat_geohash=lat_geohash,
	                    long_geohash=long_geohash
	                )

	            relay_proximity[f'wss://{relay["Relay URL"]}'] = calculated_displacement

	    relay_proximity_sorted = dict(sorted(relay_proximity.items(), key=lambda item: item[1]))
	    
	    return list(relay_proximity_sorted) 

class TestData:
	def __init__(self):
		self.GEOHASH_CHANNEL_KIND = 20000
		self.PRESENCE_KIND = 20001
		self.tags = [[], ["t", "teleport"], []]
		self.geohash = "st" 
		self.nickname = "Glazer🇵🇭 bot" 
		self.tags[0] = ["g", self.geohash]
		self.tags[2] = ["n", self.nickname]
		self.content = "nasan ang sabaw! - Baron" 

class Reader:
	def __init__(self):
		config = Config()
		self.GENERAL_HEADERS = config.GENERAL_HEADERS
		self.BITCHAT_EXPLORER_API = config.BITCHAT_EXPLORER_API

	def perform_get_request(self, url: str, specific_headers: str) -> dict | str:
	  logging.info('[*] Performing a GET request')
	  response = requests.get(url, headers=specific_headers)

	  if response.headers.get("Content-Type", "") == 'application/json; charset=utf-8':
	    return response.json()
	  else:
	    return response.text

	def main(self):
		bitLiteralChats = self.perform_get_request(url=self.BITCHAT_EXPLORER_API, specific_headers=self.GENERAL_HEADERS)
		return bitLiteralChats

class PerformRegex:
	def __init__(self):
		pass

	def translate_time_to_Filipino(self, contents: str):
		PATTERNS = {
			"second_pattern": [re.compile(r"a second ago"), "isang segundo na ang nakalipas"],
			"seconds_pattern": [re.compile(r"seconds ago"), "segundo na ang nakalipas"],
			"minute_pattern": [re.compile("a minute ago"), "isang minuto na ang nakalipas"],
			"minutes_pattern": [re.compile(r"minutes ago"), "minuto na ang nakalipas"],
			"hour_pattern": [re.compile("an hour ago"), "isang oras na ang nakalipas"],
			"hours_pattern": [re.compile("hours ago"), "oras na ang nakalipas"]

		}

		for pattern in PATTERNS:
			contents = PATTERNS[pattern][0].sub(
				PATTERNS[pattern][1],
				contents
			)
		return contents

class Bot:
	def __init__(self):
		self.nickname = "Glazer🇵🇭 Bot"
		self.MAIN_GEOHASH = "wd"
		self.GEOHASH_CHANNEL_KIND = 20000
		self.tags = [[], ["t", "teleport"], []]
		self.tags[0] = ["g", self.MAIN_GEOHASH]
		self.tags[2] = ["n", self.nickname]
		self.relays = ["wss://nostr-01.yakihonne.com"]	# inject this for compatability


		self.BLOCKED_GEOHASHES = ["hrmpzfv0z5z", "6g", "SENTRYHUB", "wd"]
		self.GEOHASH_CATEGORY_DATABASE = {
      "#st": "Egyptians",
      "#wd": "Filipinos",
      "#9q": "Americans",
      "#u2": "Europeans",
      "#xn": "Japanese",
      "ws": "Chinese",
      "wt": "Chinese",
      "d3": "Latinos",
      "qq": "Indonesians"
    }

	def frequency_geohash(self, fetched_data) -> dict:
		geohash_with_frequency= {}
		for fetched_datum in fetched_data:
			if fetched_datum["geohash"] in self.BLOCKED_GEOHASHES:
				continue
			geohash_with_frequency[fetched_datum["channel"]] = geohash_with_frequency.get(fetched_datum["channel"], 0) + 1

		descending_geohash_with_frequency = dict(sorted(geohash_with_frequency.items(), key=lambda item: item[1], reverse=True))
		desc_gh_w_frequency_list_value = {key: [value] for key, value in descending_geohash_with_frequency.items()}

		return desc_gh_w_frequency_list_value

	def make_body_frecency(self, geohash_with_frecency: dict[list]) -> str:
			body_geohash_frecency = []
			five = 0
			WRAP_WIDTH = 20

			for geohash in geohash_with_frecency:
				if five == 5:
					break
				if geohash in self.GEOHASH_CATEGORY_DATABASE:
					category_value_of_geohash = self.GEOHASH_CATEGORY_DATABASE[geohash]
					geohash_and_category = f"{geohash}\n({category_value_of_geohash})"
					chat_count_humanized = f"{geohash_with_frecency[geohash][0]} chats".ljust(WRAP_WIDTH)
					body_geohash_frecency += [[geohash_and_category, textwrap.fill(f"{chat_count_humanized}(aktibo: {geohash_with_frecency[geohash][1]})", width=WRAP_WIDTH)]]
				else:
					chat_count_humanized = f"{geohash_with_frecency[geohash][0]} chats".ljust(WRAP_WIDTH)
					body_geohash_frecency += [[geohash, textwrap.fill(f"{chat_count_humanized}(aktibo: {geohash_with_frecency[geohash][1]})", width=WRAP_WIDTH)]]
					
					pass
				five += 1

			return '\n' + tabulate(body_geohash_frecency, tablefmt="plain")

	def add_recent_to_frequency(self, geohash_with_frequency: dict, fetched_data: list):
		for a_geohash_with_frequency in geohash_with_frequency:
			temp_timestamp_list_for_a_geohash = []			

			for fetched_datum in fetched_data:
				if fetched_datum["channel"] == a_geohash_with_frequency:
					temp_timestamp_list_for_a_geohash += [fetched_datum["timestamp"]]

			recent_timestamp = temp_timestamp_list_for_a_geohash[-1]
			dt_object = datetime.fromisoformat(recent_timestamp.replace("Z", "+00:00"))
			readable_time = humanize.naturaltime(dt_object)

			p_regex = PerformRegex()
			geohash_with_frequency[a_geohash_with_frequency].append(p_regex.translate_time_to_Filipino(readable_time))
		
		return geohash_with_frequency

	def main(self):
		

		reader = Reader()
		sender = Sender()

		fetched_data_from_api = reader.main()

		frequent_geohash_list_value = self.frequency_geohash(fetched_data_from_api)
		
		concatenate_recent = self.add_recent_to_frequency(
			geohash_with_frequency=frequent_geohash_list_value, 
			fetched_data=fetched_data_from_api)

		body_frecency = self.make_body_frecency(
				concatenate_recent
			)

		print(body_frecency)

		publish_response = sender.send(
			self.GEOHASH_CHANNEL_KIND,
			self.tags,
			body_frecency,
			self.relays
		)

		print(publish_response)


if __name__ == '__main__':
	config = Config()
	PRIVATE_KEY = os.getenv("STATIC_PRIVATE_KEY")

	if not config.DEBUG:
		HeadingArt()
		while True:
			menu()


	sender = Sender()

	test_data = TestData()
	proximity = ProximityRelay()

	relay_response = sender.send(
		test_data.GEOHASH_CHANNEL_KIND,
		test_data.tags,
		test_data.content,
		proximity.find_closest_relay(test_data.geohash)
		)
	print(relay_response)

	# test = ProximityRelay()
	# print(test.find_closest_relay("wd"))

	# test = Reader()
	# print(test.main())

	# test = Bot()
	# test.main()

