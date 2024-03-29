import torch
import os
import pandas as pd
import json
import subprocess
from encoder import encode_dataframe_column
from datetime import datetime, timedelta
import logging
import argparse
import sys
import numpy as np
from time import time

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(processName)s] [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

parser = argparse.ArgumentParser(description='RSS Extraction')
parser.add_argument('--testing', type=bool, default=False, help='boolean flag for testing')
args = parser.parse_args()
testing = args.testing

bucket = "toast-encodings"
embeddings_file = 'embeddings.pth'

######### Loading in Content Json as Dataframe #########
# Load in the content lake from s3 as pandas dataframe.
os.system(f"aws s3 cp s3://toast-daily-content/content-lake.json /home/ec2-user/content-lake.json")
with open(f'/home/ec2-user/content-lake.json', 'r') as file:
    content_lake = json.load(file)
    
content_df = pd.DataFrame(content_lake)
logging.debug(f"Old Dataframe Content Lake Head: {content_df.head()}")
logging.debug(f"Length of old dataframe: {len(content_df)}")


######### Encoding Content #########
# Split dataframe into one that only has data that needs to processed
process_df = content_df[content_df["to_encode"] == True]

encoded_df = encode_dataframe_column(process_df, "content") # This needs (article id, data, and encoding.)

if encoded_df.empty:
    ######### Exiting Script #########
    logging.info("Encoding Proces Finished Exiting Instance:")
    instance_id = "i-061dff9fc11bb2250"
    os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')
    sys.exit()

######### Saving New Encodings  #########

# Download the existing embeddings file from S3
os.system(f"aws s3 cp s3://{bucket}/{embeddings_file} /home/ec2-user/{embeddings_file}")
old_embeddings = torch.load(f"/home/ec2-user/{embeddings_file}")
logging.info("encoded_df ")

# Filter out data older than 7 days
seven_days_ago = datetime.now() - timedelta(days=7)
old_data_filtered = {k: v[old_embeddings['unixTime'] >= seven_days_ago.timestamp()] for k, v in old_embeddings.items()}
old_encoded_tensor = old_data_filtered["tensor"]

new_encoded_tensor = np.array(encoded_df['tensor'].apply(lambda tensor: tensor.squeeze(0)))
new_article_id_time = torch.tensor(encoded_df['unixTime'].values)
new_article_id_tensor = torch.tensor(encoded_df['articleID'].values)

# Checks. TODO: Delete later if old data processing is looking to be a tensor.
if torch.is_tensor(old_encoded_tensor):
    logging.info("Old Vector is a tensor")
    pass
else:
    logging.info("Old Vector is not a tensor")
    logging.info(f"Old Vector is type: {type(old_encoded_tensor)}")
    old_encoded_tensor = torch.stack(list(old_encoded_tensor)) # Maybe change this.
    logging.info(f"Number of encoded old articles: {old_encoded_tensor.size()}")

if torch.is_tensor(new_encoded_tensor):
    logging.info("New Vector is a tensor")
    pass
else:
    logging.info("New Vector is not a tensor")
    logging.info(f"New Vector is type: {type(new_encoded_tensor)}")
    new_encoded_tensor = torch.stack(list(new_encoded_tensor)) # Maybe change this.
    logging.info(f"Number of encoded new articles: {new_encoded_tensor.size()}")


concatenated_embeddings = {
    'articleID': torch.cat([old_data_filtered['articleID'], new_article_id_tensor]),
    'tensor': torch.cat([old_encoded_tensor, new_encoded_tensor]),
    'unixTime': torch.cat([old_data_filtered['unixTime'], new_article_id_time])
}
logging.info(f"Number of Encoded Articles in System: {concatenated_embeddings['tensor'].size()}")
logging.info("Existing embeddings loaded and concatenated with new embeddings.")
torch.save(concatenated_embeddings, f"/home/ec2-user/{embeddings_file}")

logging.info("Wrtiting to S3")
os.system(f"aws s3 cp /home/ec2-user/{embeddings_file} s3://{bucket}/{embeddings_file}")



######### Saving Content #########
# Save original dataframe with all of the process column being true. 
content_df["to_encode"] = False # Set entire process column to False.
content_lake_dict = content_df.to_dict(orient='records')
logging.debug(f"Length of Concatenated Dictionary: {len(content_lake_dict)}")

with open(f'/home/ec2-user/content-lake.json', 'w') as file:
    json.dump(content_lake_dict, file, indent=4)

logging.info("Inserting content back to s3 after finishing encoding process.")
os.system(f"aws s3 cp /home/ec2-user/content-lake.json s3://toast-daily-content/content-lake.json")


# Delete content-lake.json and embeddings.pth from ec2-user
try:
    os.system("rm /home/ec2-user/content-lake.json")
    os.system(f"rm /home/ec2-user/{embeddings_file}")
except Exception as e:
    logging.error(f"Error: {e}")
    pass

######### Exiting Script #########
if not testing:
    try: # TODO: Remove try except blcok after vacation if calls successful
        os.system(f"aws s3 cp /tmp/git_process.log s3://production-logs-tokenized-toast/ArticleEncoding/git_logs/{str(int(time()))}.log")

        os.system(f"aws s3 cp /tmp/temp.log s3://production-logs-tokenized-toast/ArticleEncoding/working-logs/{str(int(time()))}.log")
        
        payload = '{"instance_id": "i-061dff9fc11bb2250"}'
        command = f'aws lambda invoke --function-name "toastInstances-removeLogs" --payload \'{payload}\' output.json'
        os.system(command)
        
    except: 
        pass

    logging.info("Encoding Proces Finished Exiting Instance:")
    instance_id = "i-061dff9fc11bb2250"
    os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')