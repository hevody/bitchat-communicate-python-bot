import json
import logging
import requests

def perform_get_request(url: str, specific_headers: str) -> dict | str:
  logging.info('[*] Performing a GET request')
  response = requests.get(url, headers=specific_headers)

  if response.headers.get("Content-Type", "") == 'application/json; charset=utf-8':
    return response.json()
  else:
    return response.text

def get_the_relays(bce_metadata: list) -> list:
  # for development purpose
  logging.info("[*] Fetching the relays")

  relays = []
  for metadatum in bce_metadata:
    relays += [metadatum["sourceRelay"]]

  unique_relays = list(set(relays))  
  return unique_relays

def debug_pubkey(fetched_data):
  for fetched_datum in fetched_data:
    if fetched_datum["username"] == 'not_glazer':
      print(f'{fetched_datum["geohash"]}: {fetched_datum["nostrPubkey"]}')


def main():
  with open('config.json') as f:
    config = json.load(fp=f)

  DEBUG = config["DEBUG"]

  if DEBUG:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
  else:
    logging.disable(logging.CRITICAL)


  GENERAL_HEADERS = config["GENERAL_HEADERS"]
  BITCHAT_EXPLORER_API = config["BITCHAT_EXPLORER_API"]

  bitLiteralChats = perform_get_request(url=BITCHAT_EXPLORER_API, specific_headers=GENERAL_HEADERS)
  debug_pubkey(bitLiteralChats)
  input()
  return bitLiteralChats

if __name__ == '__main__':
  main()
  
  