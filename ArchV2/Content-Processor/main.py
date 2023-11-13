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

def insert_database(article_dict:dict, table_name:str):
    '''For right now this is a two pronged s3 solution one for data retrieval with S3 and one for analytics. One day I want to move to a managed Database though.'''

    bucket = 'toast-daily-content'
    parent = f'retrieval/{article_dict["articleID"]}'
    with open(f'/home/ec2-user/article-content.json', 'w') as file:
        json.dump(article_dict, file, indent=4)

    os.system(f"aws s3 cp /home/ec2-user/article-content.json s3://{bucket}/{parent}/article-content.json")


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
content_lake = []
FEEDS = []
currentUnixTime = int(datetime.now().timestamp())
for feed in rss_feeds:
    if feed['update']:
        FEEDS.append(feed)
FEEDS = FEEDS[:100]
with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    content_archive = pool.map(worker, FEEDS)

for output in tqdm(content_archive, total=len(content_archive)):
    if output == {} or output == None:
        continue

    articles = output['articles']
    max_date = output['max_date']
    feed = output['feed']
    rss_feeds.remove(feed)

   
    
    feed['dt'] = max_date
    feed['update'] = 0
    rss_feeds.append(feed)

    for article in articles:
        
        if article == {}:
            continue
        elif article['unixTime'] == None:
            article['unixTime'] = int(datetime.now().timestamp())
        article['articleID'] = create_unique_id(unique_ids)
        article["process"] = True
        content_lake.append(article)
        print(article.keys())

        insert_database(article, 'articleContent')

#### Process Article Content
# Load in articles as pandas dataframe. 
# Check if any new articles even exist.

# if they do; Load in older article batches also as pandas dataframe. 
# Remove any articles older than 7 days
# Merge the two dataframes



############## Save Data ##############

# TODO: Save the content-lake dataframe as a json file??! Is it going to complain about some of the article content being json serializable?
# DELETE DELETe 
df = pd.DataFrame(content_lake)
content_lake_dict = df.to_dict(orient="records")

with open(f'/home/ec2-user/content-lake.json', 'w') as file:
    json.dump(content_lake_dict, file, indent=4)
os.system(f"aws s3 cp /home/ec2-user/content-lake.json s3://toast-daily-content/content-lake.json")

#### Save RSS Feed back to S3
with open(f'/home/ec2-user/{rss_file}', 'w') as file:
    json.dump(rss_feeds, file, indent=4)
os.system(f"aws s3 cp /home/ec2-user/{rss_file} s3://{bucket}/{rss_file}")

##### Save Article ID csv
updated_series = pd.Series(list(unique_ids))
updated_series.to_csv(f'/home/ec2-user/{article_id_file}', index=False, header=True)
os.system(f"aws s3 cp /home/ec2-user/{article_id_file} s3://{bucket}/{article_id_file}")