from main import (
	Reader,
	Config 
	)
import feedparser
from bs4 import BeautifulSoup
from text_fancipy.fancipy import fancipy, unfancipy_all


if __name__ == '__main__':
	news_contents = ''
	reader = Reader()
	config = Config()
	d = feedparser.parse(config.GMA_NEWS_NATION_RSS_FEED)
	# print(d["entries"])

	for entry in d["entries"]:
		# needed title, link, summary
		# print(fancipy(entry["title"], "snbd"))
		# print(entry["link"])
		summary_with_html = entry["summary"]
		soup = BeautifulSoup(summary_with_html, 'html.parser')
		br_tag = soup.find('br')
		summary = br_tag.next_sibling.strip()
		# print(f"Summary: {summary}")

		news_content = f'📰 {fancipy(entry["title"], "snbd")}\n🔎 Summary: {summary}\n🔗 Link: {entry["link"][:-1]}\n\n'
		news_contents += news_content

	return news_contents
