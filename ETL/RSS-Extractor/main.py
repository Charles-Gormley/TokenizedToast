import logging
import multiprocessing
import feedparser
import newspaper
from multiprocessing import Pool
import os
import json

from article_extraction import process_feed

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(processName)s] [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def worker(feed_url):
    logging.info(f"Processing feed: {feed_url}")
    return process_feed(feed_url)


def save_to_s3(bucket_name, file_path, s3_key):
    os.system(f'aws s3 cp {file_path} s3://{bucket_name}/{s3_key}')

def stop_ec2_instance(instance_id):
    os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')

logging.info("Main function completed")

os.chdir("/home/ec2-user/TokeizedToanst/ETL/RSS-Extractor")

# Load the JSON data from the file
with open('rss-feeds.json', 'r') as f:
    FEEDS = json.load(f)
    

with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    content_archive = pool.map(worker, FEEDS)

logging.info("Stopped concurrent processes")
from datetime import datetime

for i in content_archive:
    if i == {} or i is None:
        continue

    for j in i['articles']:
        if j == {}:
            continue
        elif j['date'] == None:
            j['date'] = 'None'
        else:
            date_str = j['date'].strftime("%Y-%m-%d")
            j['date'] = date_str

content_archive = [item for item in content_archive if item is not None]

# Amount of Feeds
pulled_feeds = len(content_archive)
logging.info("Actual Feeds: %s", str(pulled_feeds))

# Section Json Handling
logging.info("Dumping Json")
json_data = json.dumps(content_archive)
file_path = 'content.json'

os.chdir()

logging.info("Deleting old content.json file if it exists")
if os.path.exists(file_path):
    os.remove(file_path)
    print(f"{file_path} deleted successfully.")
else:
    print(f"{file_path} does not exist.")

logging.info("Writing json File")
with open(file_path, 'w') as json_file:
    json_file.write(json_data)

logging.info("Saving content.json to s3")
save_to_s3("toast-daily-content", "content.json", "content.json")

# Section: Pandas Dataframe
logging.info("Running pandas content transform")
os.system("/usr/local/bin/python3.11 /home/ec2-user/TokenizedToast/ETL/Content-Transform/main.py")

logging.info("Saving pandas dataframe to s3")
save_to_s3("toast-daily-content", "cleaned-data.pkl", "cleaned-data.pkl")

# Section: Shutting off instance
logging.info("Process Finished Shuting off ec2 instance")
stop_ec2_instance("i-0ea95298232d8ed99")
