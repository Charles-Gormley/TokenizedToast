############## Libraries #############
import json
from datetime import datetime
import os
import subprocess
import logging
from time import sleep, time
import base64

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

try: # TODO: Remove try except blcok after vacation if calls successful
    os.system(f"aws s3 cp /tmp/git_process.log s3://production-logs-tokenized-toast/Feed-Checker/git_logs/{str(int(time()))}.log")

    os.system(f"aws s3 cp /tmp/temp.log s3://production-logs-tokenized-toast/Feed-Checker/working-logs/{str(int(time()))}.log")
    
    payload_dict = {"instance_id": "i-09d0b28eb3ef19362"}

    # Convert the dictionary to a JSON string and then to bytes
    payload_bytes = json.dumps(payload_dict).encode('utf-8')

    # Base64 encode the bytes
    payload_base64 = base64.b64encode(payload_bytes).decode('utf-8')

    # Define the AWS CLI command as a list of arguments
    command = ["aws", "lambda", "invoke", 
            "--function-name", "toastInstances-removeLogs", 
            "--payload", payload_base64, 
            "output.json"]

    # Print command for debugging
    print("Executing command:", ' '.join(command))

    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True)

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
        
except: 
    pass