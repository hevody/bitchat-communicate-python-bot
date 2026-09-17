import json
import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import (	ConnectionClosed,
									InvalidStatus)
import websockets
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import send.send_message_nostr as sender
from dotenv import load_dotenv
load_dotenv()
CONFIG_FILE = './config.json'
import random
import string

# Define the length of your random name
length = 10
# Pool of letters (upper and lower case) and digits
chars = 'bcdefghkmnpqrstuvwxyz1234567890'
# Generate random string
random_name = "".join(random.choices(chars, k=length))
random_message = "".join(random.choices(chars, k=length))



with open(CONFIG_FILE) as f:
    config = json.load(fp=f)

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
tags = config["BOT_CONFIG"]["tags"]
tags[1] = ["n", random_name]
message = random_message
enable_proof_of_work = config["enable_proof_of_work"]
relays = config["RELAYS"]



with open('config.json') as f:
	settings = json.load(fp=f)

RELAYS = settings["RELAYS"]

SUBSC_RELAY_MESSAGE = json.dumps([
	"REQ", "global-bitchat",
	{"kinds": [20000]}
])


response = sender.send(PRIVATE_KEY=PRIVATE_KEY,
                      kind=20000,
                      tags=tags,
                      content=message,
                      proof_of_work=enable_proof_of_work, 
                      relays=relays)

SUBSC_RELAY_MESSAGE = ["EVENT", response]


def randomize_message():
    random_message = "".join(random.choices(chars, k=length))
    return r_message

async def client(relay):
    delay = 5

    while True:
        try:
            # print(f"Connecting to {relay}...")

            async with websockets.connect(
                relay,
                open_timeout=20,
            ) as websocket:

                random_message = "".join(random.choices(chars, k=length))
                random_geohash = "".join(random.choices(chars, k=3))
                random_name = "".join(random.choices(chars, k=10))
                # message = random_message
                message = "hacked by a Filipino"

                tags[1] = ["n", random_name]
                tags[0] = ["g", random_geohash]             
                response = sender.send(PRIVATE_KEY=PRIVATE_KEY,
                      kind=20000,
                      tags=tags,
                      content=message,
                      proof_of_work=enable_proof_of_work, 
                      relays=relays)

                SUBSC_RELAY_MESSAGE = json.dumps(["EVENT", response])
                #print(f"Connected to {relay}")
                await websocket.send(SUBSC_RELAY_MESSAGE)
                delay = 5

                # Your normal websocket work goes here
                msg = await websocket.recv()
                message_jsonify = json.loads(msg)
                print(message_jsonify)
                await asyncio.sleep(delay)
                try:
                    if message_jsonify[2]['tags'][0][1] == 'wd':
                        print(message_jsonify)
                    if message_jsonify[2]['tags'][1][1] == 'glazer':
                        print
                        print(message_jsonify)
                except: pass


        except websockets.exceptions.InvalidStatus as e:
            # print(f"{relay}: server rejected connection: {e}")

            # Don't immediately reconnect after a 429.
            await asyncio.sleep(delay)
            delay = min(delay * 2, 300)

        except (websockets.exceptions.WebSocketException,
                OSError) as e:
            # print(f"{relay}: connection error: {e}")
            await asyncio.sleep(delay)
            delay = min(delay * 2, 300)

        except asyncio.CancelledError:
            # print(f"{relay}: client cancelled")
            raise

async def main():
	await asyncio.gather(
		*(client(relay) for relay in RELAYS)
	)

if __name__ == '__main__':
	asyncio.run(main())
