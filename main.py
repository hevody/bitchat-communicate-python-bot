
import json
import os
import json
import logging

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cryptography_specific.generate_key as keygen

from dotenv import (load_dotenv,
					find_dotenv,
					set_key)
from coincurve import PrivateKey
import time
import hashlib
import websocket

DOTENV_PATH = find_dotenv()




def load_necessary_data() -> tuple[list, bool, str]:
	load_dotenv()
	with open("config.json") as f:
		config = json.load(fp=f)
	
	relays = config["RELAYS"]
	enable_proof_of_work = config["enable_proof_of_work"]
	PRIVATE_KEY = os.getenv("PRIVATE_KEY")

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

class TestData:
	def __init__(self):
		self.GEOHASH_CHANNEL_KIND = 20000
		self.PRESENCE_KIND = 20001
		self.tags = [[], ["t", "teleport"], []]
		self.geohash = "wd" 
		self.nickname = "glazer be glazing" 
		self.tags[0] = ["g", self.geohash]
		self.tags[2] = ["n", self.nickname]
		self.content = "nasan ang sabaw!" 

if __name__ == '__main__':
	config = Config()
	PRIVATE_KEY = os.getenv("STATIC_PRIVATE_KEY")

	if not config.DEBUG:
		HeadingArt()
		while True:
			menu()

	sender = Sender()
	test_crypto = CryptographySpecific()

	# pk_signer, pubkey = test_crypto.retrieve_signer_and_pubkey(PRIVATE_KEY)
	test_data = TestData()

	# mined = test_crypto.mine_nonce(	pubkey,
	# 								test_data.GEOHASH_CHANNEL_KIND,
	# 								test_data.tags,
	# 								test_data.content,
	# 								config.NONCE_DIFFICULTY)
	
	# sender.event_generator(	test_data.GEOHASH_CHANNEL_KIND,
	# 						test_data.tags,
	# 						test_data.content)

	relay_response = sender.send(
		test_data.GEOHASH_CHANNEL_KIND,
		test_data.tags,
		test_data.content,
		config.RELAYS_LEGACY
		)
	print(relay_response)