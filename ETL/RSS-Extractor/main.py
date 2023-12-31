import logging
import multiprocessing
import feedparser
import newspaper
from multiprocessing import Pool
import os
import json
import argparse
from datetime import datetime

from article_extraction import process_feed

os.system('/usr/local/bin/python3.11 /home/ec2-user/Misc/Helper-Scripts/lambda_uploader.py')
os.system('/usr/local/bin/python3.11 /home/ec2-user/Misc/Helper-Scripts/emr_uploader.py')

import argparse
# Initialize the argument parser
parser = argparse.ArgumentParser(description="Process some arguments.")

# Add the optional argument. If it's not provided, its value will be set to False.
parser.add_argument("--article_num", type=int, default=False,
                    help="Number of the article. Default is False.")
now = datetime.now()
m = str(now.month)
d = str(now.day)
y = str(now.year)
todays_str = f'{y}-{m}-{d}'

cleaned_data_fn_date = f'cleaned-data{todays_str}.pkl' # Doing this for EBS Volume Reasonings
content_json_fn_date = f'content-{y}-{m}-{d}.json'
cleaned_data_fn = 'cleaned-data.pkl'
cleaned_data_csv_fn = 'cleaned-data.csv'
content_json_fn = 'content.json'


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

os.chdir("/home/ec2-user/TokenizedToast/ETL/RSS-Extractor")

# Parse the provided arguments
args = parser.parse_args()

# Access the article_num value
set_article_num = args.article_num

# Load the JSON data from the file
with open('rss-feeds.json', 'r') as f:
    FEEDS = json.load(f)

if set_article_num:
    logging.info("Article Number Set! This is a test.")
    FEEDS = FEEDS[:set_article_num] # This is for testing purposes 

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
content_file_path = "/home/ec2-user/" + content_json_fn
df_file_path = "/home/ec2-user/" + cleaned_data_fn
csv_file_path = "/home/ec2-user/" + cleaned_data_csv_fn

logging.info("Deleting old content.json file if it exists")
if os.path.exists(content_file_path):
    os.remove(content_file_path)
    print(f"{content_file_path} deleted successfully.")
else:
    print(f"{content_file_path} does not exist.")

logging.info("Writing json File")
with open(content_file_path, 'w') as json_file:
    json_file.write(json_data)

logging.info("Saving content.json to s3")
save_to_s3("toast-daily-content", content_file_path, content_json_fn_date)

# Section: Pandas Dataframe
logging.info("Running pandas content transform")
os.system("/usr/local/bin/python3.11 /home/ec2-user/TokenizedToast/ETL/Content-Transform/main.py")

logging.info("Saving pandas dataframe to s3")
save_to_s3("toast-daily-content", df_file_path, cleaned_data_fn_date)

logging.info("Saving csv file s3")
save_to_s3("toast-daily-content", csv_file_path, cleaned_data_csv_fn)


if set_article_num != 5:
    logging.info("Process Finished Shuting off ec2 instance")
    stop_ec2_instance("i-0ea95298232d8ed99")
