import queue
import threading
import pickle
import json
from tqdm import tqdm
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


from article_extraction import extract_article
from article_extraction import extract_feed

import concurrent.futures

import os
os.chdir("C:/Users/Charl/Documents/Projects/TokenizedToast/ETL/RSS-Extractor")

# Load the JSON data from the file
with open('rss-feeds.json', 'r') as f:
    feeds = json.load(f)

# New function for processing each feed
def process_feed(feed):
    output_queue = queue.Queue()
    thread = threading.Thread(target=extract_feed, args=(feed, output_queue,))
    try:
        
        thread.daemon = True
        thread.start()
        logging.info("Thread Started: %s", feed)
        thread.join(timeout=60)
        logging.info('Thread Stopped: %s', feed)
        if thread.is_alive():
            thread.terminate()
            logging.info("Killing Thread: %s", feed)
            thread.join()
        else:
            logging.info("Successful Thread: %s", feed)
            output = output_queue.get()
    except:
        pass

    try: 
        output['articles']
        return output
    except:
        return None

def save_to_s3(bucket_name, file_path, s3_key):
    os.system(f'aws s3 cp {file_path} s3://{bucket_name}/{s3_key}')

def stop_ec2_instance(instance_id):
    os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')

# Use ThreadPoolExecutor to parallelize the workload
content_archive = []
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    for result in tqdm(executor.map(process_feed, feeds), total=len(feeds)):
        if result is not None:
            content_archive.append(result)
    executor.shutdown(wait=False)

logging.info("Amount of fees obtained") #TODO Change to successful Threads
print(len(content_archive)) # NOTE: This was 110 when timeout was 15 increasing timeout to see results.
# NOTE 40 seconds increased feed obtaining to 878. Trying again at 60 seconds. 

logging.info("Stopped concurrent processes")
from datetime import datetime

for i in content_archive:
    for j in i['articles']:
        if j == {}:
            continue
        elif j['date'] == None:
            j['date'] = 'None'
        else:
            date_str = j['date'].strftime("%Y-%m-%d")
            j['date'] = date_str

# Amount of Feeds
pulled_feeds = len(content_archive)
logging.info("Actual Feeds: %s", str(pulled_feeds))

# Section Json Handling
logging.info("Dumping Json")
json_data = json.dumps(content_archive)
file_path = 'content.json'

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
os.system("/usr/local/bin/python3.11 /home/ec2-user/Content-Transform/main.py")

logging.info("Saving pandas dataframe to s3")
save_to_s3("toast-daily-content", "cleaned-data.pkl", "cleaned-data.pkl")

# Section: Shutting off instance
logging.info("Process Finished Shuting off ec2 instance")
stop_ec2_instance("i-0ea95298232d8ed99")

