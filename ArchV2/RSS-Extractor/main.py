############## Libraries #############
import json
from datetime import datetime
import os
import logging
from time import sleep, time

from feed_checking import process_feed

############## Config #############
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Load in the rss feeds v2
bucket = 'rss-data-toast'
rss_file = 'rss_feeds_v2.json'

def save_index(i:int):
    with open("/home/ec2-user/index.txt", "w") as file:
        file.write(str(i))

def read_last_index():
    with open("/home/ec2-user/index.txt", "r") as file:
        content = file.read()
        return int(content)

try:
    index = read_last_index()
except:
    index = 0

logging.info("Log Data Cleanup")
try: # TODO: Remove try except blcok after vacation if calls successful
    os.system(f"aws s3 cp /tmp/git_process.log s3://production-logs-tokenized-toast/Feed-Checker/git_logs/{str(int(time()))}.log")

    os.system(f"aws s3 cp /tmp/temp.log s3://production-logs-tokenized-toast/Feed-Checker/working-logs/{str(int(time()))}.log")
    
    payload = '{"instance_id": "i-09d0b28eb3ef19362"}'
    command = f'aws lambda invoke --function-name "toastInstances-removeLogs" --payload \'{payload}\' output.json'
    os.system(command)
    
except: 
    pass


############## Infinite Process: Grabbing  Figure out updates of RSS Feeds. #############
while True: # Forever.
    
    # Load
    logging.info("Downloading Data from S3")
    os.system(f"aws s3 cp s3://{bucket}/{rss_file} /home/ec2-user/{rss_file}")
    with open(f'/home/ec2-user/{rss_file}', 'r') as file:
        rss_feeds = json.load(file)
    
    while index < len(rss_feeds):
        rss = rss_feeds[index]
        logging.debug(f"Index: {index}")
        
        url = rss['u']
        curUnixTime = rss['dt']

        
        if process_feed(url, curUnixTime): # Checking if new content exists.
            rss['update'] = 1
            logging.info(f"Rss Feed: {url} has new data at {curUnixTime}")
        else:
            logging.info(f"Rss Feed: {url} has no new data at {curUnixTime}")

        index += 1
        save_index(index)

        with open(f'/home/ec2-user/{rss_file}', 'w') as file:
            json.dump(rss_feeds, file, indent=4)
        os.system(f"aws s3 cp /home/ec2-user/{rss_file} s3://{bucket}/{rss_file}")
        logging.info(f"Processed URL: {url}")