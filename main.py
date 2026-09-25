import json
import logging
import os
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
from datetime import (
					datetime, 
					timezone)
import humanize
import re
from tabulate import tabulate
import textwrap
import feedparser
from bs4 import BeautifulSoup
from text_fancipy.fancipy import fancipy
import xml.etree.ElementTree as ET
from pathlib import Path

load_dotenv()

DOTENV_PATH = find_dotenv()
if DOTENV_PATH == '':
	DOTENV_PATH = Path.cwd() / ".env"
	DOTENV_PATH.touch(exist_ok=True)

REGIONS_PATH = './databases/regions.json'
BITCHAT_NOSTR_RELAY_PATH = './databases/nostr_relays.csv'

with open(REGIONS_PATH) as f:
	regions = json.load(fp=f)

PH_REGIONS = regions["PH_REGIONS"]	


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
		self.DEBUG = False
		self.POW = True
		self.LOG = True
		self.USE_STATIC_PRIVATE_KEY = True
		self.NONCE_DIFFICULTY = 8
		self.RELAYS_LEGACY = ["wss://21milionidinostr.duckdns.org", "wss://offchain.bostr.online", "wss://yabu.me", "wss://nos.lol", "wss://nostr-relay.zimage.com", "wss://nostr.twinkle.lol", "wss://nostr.2b9t.xyz", "wss://bitcoinostr.duckdns.org", "wss://nostr.dlcdevkit.com", "wss://relay01.lnfi.network", "wss://bucket.coracle.social", "wss://cdn.satellite.earth", "wss://staging.yabu.me", "wss://relay.islandbitcoin.com", "wss://nostr-relay.nextblockvending.com", "wss://nostr.whitenode45.ddns.net", "wss://no.str.cr", "wss://nostr-relay.xbytez.io", "wss://relay.illuminodes.com", "wss://relay.pyramid.li", "wss://relay.nostu.be", "wss://nostrride.io", "wss://relay.dyne.org", "wss://nostr.christiansass.de", "wss://nostr.thebiglake.org", "wss://relay02.lnfi.network", "wss://nostrrelay.taylorperron.com", "wss://relay.staging.plebeian.market", "wss://relay.guggero.org", "wss://relay.ru.ac.th", "wss://relay.damus.io", "wss://nostr.relay.hedwig.sh", "wss://nostr.myshosholoza.co.za", "wss://nostr.azzamo.net", "wss://relay.sharegap.net", "wss://relay.internationalright-wing.org", "wss://nostr-relay.corb.net", "wss://ec2.f7z.io", "wss://nostr.snowbla.de", "wss://nr.yay.so", "wss://relay1.nostrchat.io", "wss://relay.earthly.city", "wss://freelay.sovbit.host", "wss://nrl.ceskar.xyz", "wss://relay.plebeian.market", "wss://bridge.tagomago.me", "wss://offchain.pub", "wss://nostrcheck.me", "wss://relay.bowlafterbowl.com", "wss://nostr-01.yakihonne.com", "wss://nostr.4rs.nl", "wss://relay.satlantis.io", "wss://relay.mccormick.cx", "wss://adre.su", "wss://relay.laantungir.net", "wss://nostr.novacisko.cz", "wss://relay.nostrhub.fr", "wss://relay.nearhood.co.uk", "wss://nostr.unkn0wn.world", "wss://nostr.middling.mydns.jp", "wss://dev-relay.nostreon.com", "wss://myvoiceourstory.org", "wss://nostr.islandarea.net"]
		self.GENERAL_HEADERS = {
    "User-Agent": "Mozlla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Connection": "keep-alive"
  	}
		self.BITCHAT_EXPLORER_API = "https://bitchatexplorer.com/api/messages?limit=1000"
		self.PH_COMPATIBLE = True 				# turn this off if not from ph
		self.GMA_NEWS_NATION_RSS_FEED = "https://data.gmanetwork.com/gno/rss/news/nation/feed.xml"
		self.NEWS_GEOHASH = 'phnews'
		self.PAGASA_MAIN_RSS_FEED = "https://publicalert.pagasa.dost.gov.ph/feeds/"

class Sender:
	def __init__(self):
		PRIVATE_KEY = os.getenv("STATIC_PRIVATE_KEY")
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
		config = Config()
		self.PH_COMPATIBLE = config.PH_COMPATIBLE

	def calculate_displacement(self, lat_relay: float, long_relay: float, lat_geohash: float, long_geohash: float) -> float:

		displacement = math.sqrt(((lat_relay - lat_geohash)**2) + ((long_relay - long_geohash)**2))
		return displacement

	def find_closest_relay(self, geohash: str) -> list:
		relay_proximity = {}

		lat_geohash, long_geohash = pygeohash.decode(geohash=geohash)

		with open(BITCHAT_NOSTR_RELAY_PATH, mode='r', newline='', encoding='utf-8') as file:
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
		list_form_rps = list(relay_proximity_sorted) 

		if self.PH_COMPATIBLE and geohash.startswith('w'):
			list_form_rps.insert(0, "wss://nostr-01.yakihonne.com")

		return list_form_rps

class TestData:
	def __init__(self):
		self.GEOHASH_CHANNEL_KIND = 20000
		self.PRESENCE_KIND = 20001
		self.tags = [[], ["t", "teleport"], []]
		self.geohash = "phnews" 
		self.nickname = "Glazer🇵🇭 bot" 
		self.tags[0] = ["g", self.geohash]
		self.tags[2] = ["n", self.nickname]
		self.content = "nasan ang sabaw!"

class Reader:
	def __init__(self):
		config = Config()
		self.GENERAL_HEADERS = config.GENERAL_HEADERS
		self.BITCHAT_EXPLORER_API = config.BITCHAT_EXPLORER_API
		self.GET_TIMEOUT = 30

	def perform_get_request(self, url: str, specific_headers: str) -> dict | str | bool:
		logging.info('[*] Performing a GET request')
		try: 
			response = requests.get(url, headers=specific_headers, timeout=self.GET_TIMEOUT)
		except requests.exceptions.Timeout:
			return False

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
			"now_pattern": [re.compile(r"now"), "ngayon (posibleng raid)"],
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

class RSS_XML_Reader:
	def __init__(self):
		config = Config()
		self.GMA_NEWS_NATION_RSS_FEED = config.GMA_NEWS_NATION_RSS_FEED
		self.PAGASA_MAIN_RSS_FEED = config.PAGASA_MAIN_RSS_FEED
		self.GENERAL_HEADERS = config.GENERAL_HEADERS
		self.reader = Reader()

	def pagasa_by_region(self, entry_link: str):
		region_report = Reader().perform_get_request(entry_link, Config().GENERAL_HEADERS)
		root = ET.fromstring(region_report)
		
		ns = {'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}
		identifier = root.find('cap:identifier', ns)

		for info in root.findall('cap:info', ns):
			headline = info.find('cap:headline', ns)
			description = info.find('cap:description', ns)
			instruction = info.find('cap:instruction', ns)

			return f"📢 {headline.text}\n🌤️🌧️💨🌨️ Description: {description.text}\n⚠️ Instruction: {instruction.text}\n"

	def humanize_the_time(self, iso_time: str):
		dt = datetime.fromisoformat(iso_time)
		now = datetime.now(timezone.utc)
		relative_time = humanize.naturaltime(now - dt)
		return relative_time

	def concatenate_link_content(self, categorized: dict):
		region_and_its_content = {}
		for region in categorized:
			for entry in categorized[region]:
				headers = f"{fancipy(entry[1], 'snbd')}\n🗓️ Updated: {entry[2]}\n\n"
				body = self.pagasa_by_region(entry_link=entry[0])
				region_and_its_content[region] = headers + body
		return region_and_its_content

	def categorizing_metadata_to_region(self, d: list[dict]):
		categorized_metadata = {}
		for region in PH_REGIONS:
			region_pattern = re.compile(re.escape(PH_REGIONS[region][2]))
			found_recent = False
			for entry in d["entries"]:
				if found_recent:
					continue
				if bool(re.search(region_pattern, entry["title"])):
					humanized_time = self.humanize_the_time(entry["updated"])
					categorized_metadata[region] = categorized_metadata.get(region, []) + [[entry["links"][0]["href"], entry["title"], humanized_time]]
					found_recent = True
		return categorized_metadata

	def fetch_gma_ph_news(self):
		news_contents = ''
		
		d = feedparser.parse(self.GMA_NEWS_NATION_RSS_FEED)

		for entry in d["entries"]:
			summary_with_html = entry["summary"]
			soup = BeautifulSoup(summary_with_html, 'html.parser')
			br_tag = soup.find('br')
			summary = br_tag.next_sibling.strip()

			news_content = f'📰 {fancipy(entry["title"], "snbd")}\n🔎 Summary: {summary}\n🔗 Link: {entry["link"][:-1]}\n\n'
			news_contents += news_content

		return '\n' + news_contents + '\nSource: GMA News\n\nBack to #wd'

	def get_pag_asa_region_contents(self) -> dict:
		d = feedparser.parse(Config().PAGASA_MAIN_RSS_FEED)
		categorized_from_main_pagasa = self.categorizing_metadata_to_region(d=d)

		return self.concatenate_link_content(categorized_from_main_pagasa)

class Bot:
	# this bot will be sending a message every 30 minutes (ex. 2:00, 2:30, 3:00) based on GitHub actions
	def __init__(self):
		self.nickname = "Glazer🇵🇭 Bot"
		self.MAIN_GEOHASH = "wd"
		self.SUBGEOHASH = "wd1"
		self.GEOHASH_CHANNEL_KIND = 20000
		self.tags = [[], ["t", "teleport"], []]
		self.tags[0] = ["g", self.MAIN_GEOHASH]
		self.tags[2] = ["n", self.nickname]


		self.BLOCKED_GEOHASHES = ["SENTRYHUB", "wd", "test", "phnews", "sentryhub"]
		self.GEOHASH_CATEGORY_DATABASE = {
      "#st": "Egyptians",
      "#wd": "Filipinos",
      "#9q": "Americans",
      "#u2": "Europeans",
      "#xn": "Japanese",
      "#ws": "Chinese",
      "#wt": "Chinese",
      "#d3": "Latinos",
      "#qq": "Indonesians",
      "#u1": "French",
      "#tt": "Pakistanis",
			"#6g": "Brazilians"
    }

		self.BLOCKED_PUBKEYS = [
			"ad8224492887a4b66795d0a8026a201226aeae67548631586d7a83dd40bf2707",
			"a13d0cca4316d76227dcaabc59d22a0bd63ad73d723355c3645c66408dc9223a"
			]

	def frequency_geohash(self, fetched_data) -> dict:
		geohash_with_frequency= {}
		for fetched_datum in fetched_data:
			if fetched_datum["nostrPubkey"] in self.BLOCKED_PUBKEYS:
				continue
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
	
	def send_current_pagasa_advisory(self) -> list[list]:
		cached_ph_region_pagasa_contents = RSS_XML_Reader().get_pag_asa_region_contents()
		weather_region_geohash = []
		for ph_region in PH_REGIONS:
			for region_pagasa_mentionded in cached_ph_region_pagasa_contents:
				if region_pagasa_mentionded == ph_region:								
					weather_tags = self.tags
					weather_tags[0] = ["g", PH_REGIONS[ph_region][1]]

					weather_response = Sender().send(
						self.GEOHASH_CHANNEL_KIND,
						weather_tags,
						'\n' + cached_ph_region_pagasa_contents[region_pagasa_mentionded] + '\nSource: PAGASA (Philippine Atmospheric, Geophysical and Astronomical Services Administration)\n\nBack to #wd',
						ProximityRelay().find_closest_relay(self.MAIN_GEOHASH)
					)

	def body_current_pagasa_advisory(self) -> list[list]:
		cached_ph_region_pagasa_contents = RSS_XML_Reader().get_pag_asa_region_contents()
		weather_region_geohash = []
		for ph_region in PH_REGIONS:
			for region_pagasa_mentionded in cached_ph_region_pagasa_contents:
				if region_pagasa_mentionded == ph_region:								
					weather_tags = self.tags
					weather_tags[0] = ["g", PH_REGIONS[ph_region][1]]
					weather_region_geohash += [[textwrap.fill(ph_region, width=15), f'#{PH_REGIONS[ph_region][1]}']]
		return tabulate(weather_region_geohash, tablefmt="plain")

	def stop_feature_message(self):
		WRAP_WIDTH = 20
		header_message = "Pansamantalang ihinto ang bot? ⛔\n"
		body_message_list = [[".stop", textwrap.fill("Ihinto ang bot sa loob ng isang oras", width=WRAP_WIDTH)],
		                     [".override", textwrap.fill("Huwag pansininin ang naunang .stop na command", WRAP_WIDTH)]]

		return header_message + tabulate(body_message_list, tablefmt="plain")

	def heading_body_footer_send(self, sub_geohash=False):
		if sub_geohash:
			heading_initial = f"\n👋 Tropa, kumusta ang buhay buhay? Ikaw ay nasa #{self.SUBGEOHASH}, ang sub-geohash channel ng Pilipinas! 🗺️🇵🇭🌊🌺🛺"
		else:
			heading_initial = f"\n👋 Maligayang pagdating sa #{self.MAIN_GEOHASH}, ang main geohash channel ng Pilipinas! 🗺️🇵🇭🌊🌺🛺"
		
		heading = f""" 

Ako si Glazer 🦊 Isang bot na dinevelop ng isang Filipino:3 Para sa Pilipinas, para sa kapuwa Filipino .𖥔 ݁ ˖ִ🛸༄˖°.

Narito ako upang kayo ay magabayan sa pasikot-sikot ng BitChat app at upang magbahagi rin ng mga mahahalagang impormasyong may kinalaman sa Pilipinas at sa kapakanan nating mga magkababayang Filipino. 😉
"""
		self.tips = """
📌 Karaniwang tips sa paggamit ng BitChat:
	1. I-enable ang Proof of Work. Recommended: 15 bits of difficulty. 
	2. Huwag bastos. Iwasan ang pagiging seksuwal at panghaharas. 
	3. Panatilihin pa rin ang pagiging magalang. Huwag toxic.
	4. Huwag magbabahagi ng anumang impormasyon patungkol sa passwords, OTP, o anumang bagay na may kinalamam sa pera. 
	5. Gamitin ang !help command: credits to glub.chat 

"""
		body_frecency_heading = "Makihalubilo rin sa mga geohashes na ito 🥂💬 :\n(click the blue geohashes)\n"
		
		fetched_data_from_api = Reader().main()
		if not fetched_data_from_api:
			body_frecency = ""
			body_frecency_heading = ""
		else:
			frequent_geohash_list_value = self.frequency_geohash(fetched_data_from_api)
			concatenate_recent = self.add_recent_to_frequency(
				geohash_with_frequency=frequent_geohash_list_value, 
				fetched_data=fetched_data_from_api)
			body_frecency = self.make_body_frecency(
				concatenate_recent
			)

		pagasa_header = "\n\nMaging updated sa lagay ng panahon 🌊🌳🌦️⛰️🏞️ :\n(click the blue geohashes)\n\n"

		footer = """

Huwag pahuhuli sa balita 🗞 :
(click the blue geohash)
#phnews


!! Mabuhay Filipino Devs 👨🏻‍💻 !!

made with ❤️ for Filipinos by Velocity🐼



⏳ ang chat na ito ay sinesend lamang tuwing 30 minuto (Halimbawa: 2:47, 3:17, 3:47)
"""

		return heading_initial + heading + self.tips + body_frecency_heading + body_frecency + pagasa_header + self.body_current_pagasa_advisory() + footer
		# return heading + self.tips + pagasa_header + self.body_current_pagasa_advisory() + footer


		


	def main(self, sub_geohash=False) -> list:		# return a list from the nostr relay's response
		reader = Reader()
		sender = Sender()
		proximity = ProximityRelay()
		config = Config()
		r_x_reader = RSS_XML_Reader()

		message_wd = self.heading_body_footer_send(sub_geohash=sub_geohash)
		if sub_geohash:
			self.tags[0] = ["g", self.SUBGEOHASH]
		else:
			self.tags[0] = ["g", self.MAIN_GEOHASH]
		
		# sending content to wd
		wd_publish_response = sender.send(
			self.GEOHASH_CHANNEL_KIND,
			self.tags,
			message_wd,
			proximity.find_closest_relay(self.MAIN_GEOHASH)
		)
		

		# sending news
		self.tags[0] = ["g", config.NEWS_GEOHASH]
		news_publish_response = sender.send(
			self.GEOHASH_CHANNEL_KIND,
			self.tags,
			r_x_reader.fetch_gma_ph_news(),
			[proximity.find_closest_relay(config.NEWS_GEOHASH)[1]]
		)
		
		# sends pagasa advisory
		self.send_current_pagasa_advisory()

		# sending news was sent confirmation
		self.tags[0] = ["g", self.MAIN_GEOHASH]
		news_aware_publish_response = sender.send(
			self.GEOHASH_CHANNEL_KIND,
			self.tags,
			f"\n[*] Matagumpay na nakapagbahagi ng balita mula sa Pilipinas ang bot\nBisitahin ang geohash na ito: #phnews\n\n[*] Matagumpay ring nakapagbahagi ng abiso patungkol sa lagay ng panahon.\nBasahin ang nasa itaas.\n\nOpen BitChat or other geohash Nostr clients for a more seamless experience.\nRead my blog: hevody.github.io/velocity-labs/bitchat-blog\n\n{self.stop_feature_message()}",
			proximity.find_closest_relay(self.MAIN_GEOHASH)
		)
		
		return news_aware_publish_response


if __name__ == '__main__':
	config = Config()

	if not config.DEBUG:
		HeadingArt()
		while True:
			menu()
