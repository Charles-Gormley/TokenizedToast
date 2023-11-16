import json
from datetime import datetime, timedelta
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
    logging.info("Inserting content to s3 retrieval.")
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
    series = series.squeeze()
    unique_ids = set(series.tolist())  # Convert to set
    

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
        logging.info("Starting Process of Processing new article")
        if article == {}:
            continue
        elif article['unixTime'] == None:
            article['unixTime'] = int(datetime.now().timestamp())
        logging.info("Processing Article")
        article['articleID'] = create_unique_id(unique_ids)
        article["process"] = True
        content_lake.append(article)
        print(article.keys())

        insert_database(article, 'articleContent')
        logging.info("Finished Processing Article", article['articleID'])

############## Save Data ##############

# First Working time
new_df = pd.DataFrame(content_lake)
content_lake_dict = new_df.to_dict(orient='records')
with open(f'/home/ec2-user/content-lake.json', 'w') as file:
    json.dump(content_lake_dict, file, indent=4)
logging.info("Inserting content to s3 for content analytics")
os.system(f"aws s3 cp /home/ec2-user/content-lake.json s3://toast-daily-content/content-lake.json")

# #### Process & Save Article Content
# new_df = pd.DataFrame(content_lake)
# if not new_df.empty: # Check if any new articles even exist.
#     os.system(f"aws s3 cp s3://toast-daily-content/content-lake.json /home/ec2-user/content-lake.json")
#     with open(f'/home/ec2-user/content-lake.json', 'r') as file:
#         old_content_lake = json.load(file)
#     df = pd.DataFrame(old_content_lake)
#     seven_days_ago = datetime.now() - timedelta(days=7)
#     df = df[df['unixTime'] >= seven_days_ago.timestamp()]
#     concatenated_df = pd.concat([df, new_df], ignore_index=True)
#     content_lake_dict = concatenated_df.to_dict(orient='records')
#     with open(f'/home/ec2-user/content-lake.json', 'w') as file:
#         json.dump(content_lake_dict, file, indent=4)
#     logging.info("Inserting content to s3 for content analytics")
#     os.system(f"aws s3 cp /home/ec2-user/content-lake.json s3://toast-daily-content/content-lake.json")

# #### Save RSS Feed back to S3
with open(f'/home/ec2-user/{rss_file}', 'w') as file:
    json.dump(rss_feeds, file, indent=4)
os.system(f"aws s3 cp /home/ec2-user/{rss_file} s3://{bucket}/{rss_file}")

##### Save Article ID csv
updated_series = pd.Series(list(unique_ids))
updated_series.to_csv(f'/home/ec2-user/{article_id_file}', index=False, header=True)
os.system(f"aws s3 cp /home/ec2-user/{article_id_file} s3://{bucket}/{article_id_file}")