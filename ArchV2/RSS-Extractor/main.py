import json
from datetime import datetime
import os
from time import sleep

from feed_checking import process_feed

# Load in the rss feeds v2
bucket = 'rss-data-toast'
rss_file = 'rss_feeds_v2.json'

while True: # Forever.
    
    # Load
    os.system(f"aws s3 cp s3://{bucket}/{rss_file} /home/ec2-user/{rss_file}")
    with open(f'/home/ec2-user/{rss_file}', 'r') as file:
        rss_feeds = json.load(file)

    # Process
    for i, rss in enumerate(rss_feeds):
        url = rss['u']
        curUnixTime = rss['dt']

        if process_feed(url, curUnixTime): # Checking if new content exists.
            rss['update'] = 1

    # Save
    with open(f'/home/ec2-user/{rss_file}', 'w') as file:
        json.dump(rss_feeds, file, indent=4)
    os.system(f"aws s3 cp /home/ec2-user/{rss_file} s3://{bucket}//{rss_file}")
    
    sleep(2*60)