from main import (
	Reader,
	Config 
	)
import feedparser
from bs4 import BeautifulSoup
from text_fancipy.fancipy import fancipy, unfancipy_all


def fetch_gma_ph_news():
	news_contents = ''
	config = Config()
	d = feedparser.parse(config.GMA_NEWS_NATION_RSS_FEED)

	for entry in d["entries"]:
		summary_with_html = entry["summary"]
		soup = BeautifulSoup(summary_with_html, 'html.parser')
		br_tag = soup.find('br')
		summary = br_tag.next_sibling.strip()

		news_content = f'📰 {fancipy(entry["title"], "snbd")}\n🔎 Summary: {summary}\n🔗 Link: {entry["link"][:-1]}\n\n'
		news_contents += news_content

	return news_contents
