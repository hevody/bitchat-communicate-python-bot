import json
import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

with open('settings.json') as f:
	settings = json.load(fp=f)

RELAYS = settings["RELAYS"]

SUBSC_RELAY_MESSAGE = json.dumps([
	"REQ", "global-bitchat",
	{"kinds": [20000]}
])


async def client(relay: str):
	async for websocket in connect(relay):
		try:
			await websocket.send(SUBSC_RELAY_MESSAGE)
			msg = await websocket.recv()

			message_jsonify = json.loads(msg)
			print(message_jsonify)
		except ConnectionClosed:
			continue

async def main():
	await asyncio.gather(
		*(client(relay) for relay in RELAYS)
	)

if __name__ == '__main__':
	asyncio.run(main())
