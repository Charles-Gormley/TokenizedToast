############## Libraries #############
import json
from datetime import datetime
import os
import logging
from time import sleep

from feed_checking import process_feed

############## Config #############
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Load in the rss feeds v2
bucket = 'rss-data-toast'
rss_file = 'rss_feeds_v2.json'


############## Infinite Process: Grabbing  Figure out updates of RSS Feeds. #############
while True: # Forever.
    
    # Load
    logging.info("Downloading Data from S3")
    os.system(f"aws s3 cp s3://{bucket}/{rss_file} /home/ec2-user/{rss_file}")
    with open(f'/home/ec2-user/{rss_file}', 'r') as file:
        rss_feeds_unchanging = json.load(file)

    # Process
    logging.info("Processing Feeds")
    for i, _ in enumerate(rss_feeds_unchanging):

        # We gotta do this cause it will just keep updating the same data structure to the content processor if not. If we don't do this it will upload the same rss, the content processor will process the data. but the same data strucutre will be uploaded again acting like, nothing was ever changed.
        logging.info("Downloading Data from S3")
        os.system(f"aws s3 cp s3://{bucket}/{rss_file} /home/ec2-user/{rss_file}")
        with open(f'/home/ec2-user/{rss_file}', 'r') as file:
            rss_feeds = json.load(file)

        rss = rss_feeds[i]

        url = rss['u']
        curUnixTime = rss['dt']

        if process_feed(url, curUnixTime): # Checking if new content exists.
            rss['update'] = 1

        with open(f'/home/ec2-user/{rss_file}', 'w') as file:
            json.dump(rss_feeds, file, indent=4)
        os.system(f"aws s3 cp /home/ec2-user/{rss_file} s3://{bucket}/{rss_file}")
        logging.info(f"Processed URL: {url}")

        

    logging.info("Sleeping")
    sleep(2*60) # TODO: Shutoff then shut back on automated process.