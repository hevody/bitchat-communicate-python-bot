import json
import asyncio 
import websockets.exceptions 
import websockets

CONFIG_PATH = './legacy/config.json'

with open(CONFIG_PATH) as f:
	settings = json.load(fp=f)

RELAYS = settings["RELAYS"]

SUBSC_RELAY_MESSAGE = json.dumps([
	"REQ", "global-bitchat",
	{"kinds": [20000]}
])

async def client(relay):
    delay = 5

    while True:
        try:
            # print(f"Connecting to {relay}...")

            async with websockets.connect(
                relay,
                open_timeout=20,
            ) as websocket:

                # print(f"Connected to {relay}")
                await websocket.send(SUBSC_RELAY_MESSAGE)
                delay = 5

                # Your normal websocket work goes here
                msg = await websocket.recv()
                message_jsonify = json.loads(msg)
                # try:
                #     if message_jsonify[2]['tags'][0][1] == 'wd':
                #         print(message_jsonify)
                #     if message_jsonify[2]['tags'][1][1] == 'glazer':
                #         print
                #         print(message_jsonify)
                # except: pass
                print(message_jsonify)


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
