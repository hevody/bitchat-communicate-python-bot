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

def main():
  pass

if __name__ == '__main__':
  with open('settings.json') as f:
    settings = json.load(fp=f)

  debug = settings["debug"]

  GENERAL_HEADERS = settings["GENERAL_HEADERS"]
  BITCHAT_EXPLORER_API = settings["BITCHAT_EXPLORER_API"]

  bitLiteralChats = perform_get_request(url=BITCHAT_EXPLORER_API, specific_headers=GENERAL_HEADERS)
  print(bitLiteralChats)
  