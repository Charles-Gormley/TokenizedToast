import json
from datetime import datetime, timedelta
import os
from time import sleep, time
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
    logging.debug(f'Processing feed {feed_url}')
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
rss_file = 'rss_feeds_v2.json'

os.system(f"aws s3 cp s3://{bucket}/{rss_file} /home/ec2-user/{rss_file}")
with open(f'/home/ec2-user/{rss_file}', 'r') as file:
    rss_feeds = json.load(file)

# Removing Duplicates if they exist.
rss_feeds_df = pd.DataFrame(rss_feeds)
rss_feeds_df = rss_feeds_df.drop_duplicates()
rss_feeds = rss_feeds_df.to_dict('records')
logging.info(f"Amount of rss_feeds after processing: {len(rss_feeds)}")
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
for feed in rss_feeds:
    FEEDS.append(feed)

if testing:
    FEEDS = FEEDS[-90:]    

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
        
        logging.debug("Processing Article")
        article['articleID'] = create_unique_id(unique_ids)
        logging.debug(f"Starting Process of Processing new article {article['articleID']}")
        article["process"] = True
        content_lake.append(article)

        insert_database(article, 'articleContent')
        logging.debug(f"Finished Processing Article {article['articleID']}")

logging.info(f"Amount of rss_feeds after processing: {len(rss_feeds)}")
logging.info(f"Amount of Articles Processed: {len(content_lake)}")
############## Save Data ##############

# #### Process & Save Article Content
new_df = pd.DataFrame(content_lake)
logging.info(f"Length of Content Lake: {len(content_lake)}")
logging.info(f"New Dataframe Content Lake Head: {new_df.head()}")
logging.info(f"Length of new dataframe: {len(new_df)}")
new_df["to_encode"] = True

if not new_df.empty: # Check if any new articles even exist.

    try: # Incase the content lake is empty
        os.system("rm /home/ec2-user/content-lake.json")
        os.system(f"aws s3 cp s3://toast-daily-content/content-lake.json /home/ec2-user/content-lake.json")
        with open(f'/home/ec2-user/content-lake.json', 'r') as file:
            old_content_lake = json.load(file)
        
        df = pd.DataFrame(old_content_lake)
        try:
            print(df["to_encode"])
        except:
            df["to_encode"] = True # This column does not exists.

        old_df_size = len(df)

        logging.info(f"Old Dataframe Content Lake Head: {df.head()}")
        logging.info(f"Length of old dataframe: {old_df_size}")
        
        seven_days_ago = datetime.now() - timedelta(days=7)
        df = df[df['unixTime'] >= seven_days_ago.timestamp()]

        new_df_size = len(df)
        logging.info(f"Amount of data points removed from date check: {old_df_size-new_df_size}")

        concatenated_df = pd.concat([df, new_df], ignore_index=True)
    except:
        concatenated_df = new_df
    
    logging.info(f"Length of Concatenated Dataframe: {len(concatenated_df)}")
    content_lake_dict = concatenated_df.to_dict(orient='records')
    logging.info(f"Length of Concatenated Dictionary: {len(content_lake_dict)}")

    with open(f'/home/ec2-user/content-lake.json', 'w') as file:
        json.dump(content_lake_dict, file, indent=4)
    
    logging.info("Inserting content to s3 for content analytics")
    os.system(f"aws s3 cp /home/ec2-user/content-lake.json s3://toast-daily-content/content-lake.json")

# #### Save RSS Feed back to S3
# Removing Duplicates if they exist.
logging.info("Saving RSS Feeds to S3")
rss_feeds_df = pd.DataFrame(rss_feeds)
rss_feeds_df = rss_feeds_df.drop_duplicates()
rss_feeds = rss_feeds_df.to_dict('records')
with open(f'/home/ec2-user/{rss_file}', 'w') as file:
    json.dump(rss_feeds, file, indent=4)
os.system(f"aws s3 cp /home/ec2-user/{rss_file} s3://{bucket}/{rss_file}")

##### Save Article ID csv
logging.info("Saving Unique Article IDs to S3")
updated_series = pd.Series(list(unique_ids))
updated_series.to_csv(f'/home/ec2-user/{article_id_file}', index=False, header=True)
os.system(f"aws s3 cp /home/ec2-user/{article_id_file} s3://{bucket}/{article_id_file}")

if not testing: # If we are not in testing mode I want the instance to shut off.
    logging.info("Invoking Encoding Lambda")
    os.system('aws lambda invoke --function-name "StartEncodingJob" lambda_output.txt')

    logging.info("Invoking RSS Extraction lambda Lambda")
    os.system('aws lambda invoke --function-name "RSSExtractionFlickerBackOn" lambda_output.txt')

    try: # TODO: Remove try except blcok after vacation if calls successful
        os.system(f"aws s3 cp /tmp/git_process.log s3://production-logs-tokenized-toast/ArticleExtraction/git_logs/{str(int(time()))}.log")
        os.system(f"aws s3 cp /tmp/temp.log s3://production-logs-tokenized-toast/ArticleExtraction/working-logs/{str(int(time()))}.log")

        payload = '{"instance_id": "i-0ea95298232d8ed99"}'
        command = f'aws lambda invoke --function-name "toastInstances-removeLogs" --payload \'{payload}\' output.json'
        logging.info(command)
        os.system(command)

    except: 
        pass

    logging.info("Process Finished Shuting off ec2 instance")
    instance_id = "i-0ea95298232d8ed99"
    os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')
