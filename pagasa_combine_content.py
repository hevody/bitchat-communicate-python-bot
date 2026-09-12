import main
import xml.etree.ElementTree as ET
import feedparser
import json
import re
from datetime import datetime, timezone
import humanize
from text_fancipy.fancipy import fancipy

with open('regions.json') as f:
	regions = json.load(fp=f)

PH_REGIONS = regions["PH_REGIONS"]

def fetch_pagasa_main(d: dict):
	# we need the Title, link, time updated,
	for entry in d["entries"]:
		print(entry["title"])				# title
		print(entry["updated"])				# last updated
		print(entry["links"][0]["href"])	# links
		print("=====")

def pagasa_by_region(entry_link: str):
	reader = main.Reader()
	config = main.Config()
	region_report = reader.perform_get_request(entry_link, main.Config().GENERAL_HEADERS)
	root = ET.fromstring(region_report)
	
	
	ns = {'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}
	identifier = root.find('cap:identifier', ns)

	for info in root.findall('cap:info', ns):
	    headline = info.find('cap:headline', ns)
	    description = info.find('cap:description', ns)
	    instruction = info.find('cap:instruction', ns)

	    return f"📢 {headline.text}\n🌤️🌧️💨🌨️ Description: {description.text}\n⚠️ Instruction: {instruction.text}\n"

def humanize_the_time(iso_time: str):
	dt = datetime.fromisoformat(iso_time)
	now = datetime.now(timezone.utc)
	relative_time = humanize.naturaltime(now - dt)
	return relative_time

def concatenate_link_content(categorized: dict):
	region_and_its_content = {}
	for region in categorized:
		for entry in categorized[region]:
			headers = f"{fancipy(entry[1], 'snbd')}\n🗓️ Updated: {entry[2]}\n\n"
			body = pagasa_by_region(entry_link=entry[0])
			region_and_its_content[region] = headers + body
	print(region_and_its_content)

def categorizing_metadata_to_region(d: list[dict]):
	categorized_metadata = {}
	for region in PH_REGIONS:
		region_pattern = re.compile(re.escape(PH_REGIONS[region][2]))
		found_recent = False
		for entry in d["entries"]:
			if found_recent:
				continue
			if bool(re.search(region_pattern, entry["title"])):
				humanized_time = humanize_the_time(entry["updated"])
				categorized_metadata[region] = categorized_metadata.get(region, []) + [[entry["links"][0]["href"], entry["title"], humanized_time]]
				found_recent = True
	return categorized_metadata

if __name__ == '__main__':
	# pagasa_by_region()
	# input()

	d = feedparser.parse(main.Config().PAGASA_MAIN_RSS_FEED)		# for caching
	categorized_from_main_pagasa = categorizing_metadata_to_region(d=d)
	
	concatenate_link_content(categorized_from_main_pagasa)
