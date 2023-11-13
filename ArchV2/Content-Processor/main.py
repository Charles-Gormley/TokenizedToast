import json
from datetime import datetime
import os
from time import sleep
from random import randint
import multiprocessing
import argparse
import logging

from article_extraction import process_feed

import pandas as pd
from tqdm import tqdm

############## Argument Parsing #############
parser = argparse.ArgumentParser(description='RSS Extraction')
parser.add_argument('--testing', type=bool, default=False, help='boolean flag for testing')
args = parser.parse_args()
testing = args.testing

### Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(processName)s] [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


############## Functions (Move Later) #############
def create_unique_id(unique_ids:set) -> int:
    id = randint(100000000, 999999999)
    while id in unique_ids:
        id = randint(100000000, 999999999)
    unique_ids.add(id)
    return id

def worker(feed_url):
    logging.info(f'Processing feed {feed_url}')
    return process_feed(feed_url)

def insert_dynamo(article_dict:dict, table_name:str):
    cmd = f"aws dynamodb put-item --table-name {table_name} --item '{json.dumps(article_dict)}'"
    os.system(cmd)

############## Load in Data #############
bucket = 'rss-data-toast'

##### RSS Feeds
if testing:
    rss_file = 'sample_rss_feeds.json'
else:
    rss_file = 'rss_feeds_v2.json'

os.system(f"aws s3 cp s3://{bucket}/{rss_file} /home/ec2-user/{rss_file}")
with open(f'/home/ec2-user/{rss_file}', 'r') as file:
    rss_feeds = json.load(file)

##### Load in article IDS
article_id_file = 'unique_article_ids.csv'
os.system(f"aws s3 cp s3://{bucket}/{article_id_file} /home/ec2-user/{article_id_file}")
with open(f'/home/ec2-user/{article_id_file}', 'r') as file:
    series = pd.read_csv(file) # Pandas Series
    print(series)
    print(series.columns)
    series = series.squeeze()
    unique_ids = set(series.tolist())  # Convert to set
    print(unique_ids)

############## Process Data #############
FEEDS = []
currentUnixTime = int(datetime.now().timestamp())
for feed in rss_feeds:
    if feed['update']:
        FEEDS.append(feed)

with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    content_archive = pool.map(worker, FEEDS)

for output in tqdm(content_archive, total=len(content_archive)):
    if output == {} or output == None:
        continue

    articles = output['articles']
    max_date = output['max_date']
    feed = output['feed']
    print(feed)
    
    rss_feeds.remove(feed)
    
    feed['dt'] = max_date
    feed['update'] = 0
    rss_feeds.append(feed)

    for article in articles:
        if article == {}:
            continue
        elif article['date'] == None:
            article['date'] = int(datetime.now().timestamp())
        article['articleID'] = create_unique_id(unique_ids)
        article["process"] = True
        article['partition'] = 0
        logging.debug(f'Feed url Now: {feed}')
        logging.debug(f"Inserted into: Database: {article}")
        insert_dynamo(article, 'articleContent')

############## Save Data ##############

##### Save RSS Feed back to S3
for item in rss_feeds:
    item['update'] = 1
with open(f'/home/ec2-user/{rss_file}', 'w') as file:
    json.dump(rss_feeds, file, indent=4)
os.system(f"aws s3 cp /home/ec2-user/{rss_file} s3://{bucket}/{rss_file}")

##### Save Article ID csv
updated_series = pd.Series(list(unique_ids))
updated_series.to_csv(f'/home/ec2-user/{article_id_file}', index=False, header=True)
os.system(f"aws s3 cp /home/ec2-user/{article_id_file} s3://{bucket}/{article_id_file}")