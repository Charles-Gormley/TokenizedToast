import pandas
import json
from datetime import datetime
import feedparser
from tqdm import tqdm

import feed_checking

import os
from datetime import datetime

with open('rss-feeds.json', 'r') as file:
    rss_feeds = json.load(file)


current_time = datetime.now()
currentUnixTime = int(current_time.timestamp())
updated_feeds = [{"u": url, "dt": currentUnixTime} for url in rss_feeds if url != 0]

i = 0
for i, rss in tqdm(enumerate(updated_feeds), total=len(updated_feeds)):
    url = rss['u']
    rss['dt'] = currentUnixTime
    
    if feed_checking.process_feed(url, currentUnixTime) == None:
        updated_feeds.remove(rss)

for i, rss in enumerate(updated_feeds):
    url = rss['u']
    rss['dt'] = currentUnixTime
    rss['update'] = 1  # Meaning False

with open('rss_feeds_v2.json', 'w') as file:
    json.dump(updated_feeds, file, indent=4)
