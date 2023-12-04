import torch
import os
import pandas as pd
import json
import subprocess
from encoder import encode_dataframe_column
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] [%(processName)s] [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

bucket = "toast-encodings"
encoded_df_file = "encoded_df.feather"
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


######### Saving New Encoding Dataframe #########
try: 
    os.system(f"aws s3 cp s3://{bucket}/{encoded_df_file} /home/ec2-user/{encoded_df_file}")
    old_encoded_df = pd.read_feather(f"/home/ec2-user/{encoded_df_file}")
    seven_days_ago = datetime.now() - timedelta(days=7) 
    old_encoded_df = old_encoded_df[old_encoded_df['unixTime'] >= seven_days_ago.timestamp()] # Get rid of older encodings

    concatenated_df = pd.concat([encoded_df, old_encoded_df], ignore_index=True)
    logging.info("Not the first time this is being loaded in.")
except Exception as e:
    logging.debug(f"{e}")
    logging.info("First Time Using Encodings")
    concatenated_df = encoded_df

concatenated_df.to_feather(f"/home/ec2-user/{encoded_df_file}") # Save Encoded Dataframe.
os.system(f"aws s3 cp /home/ec2-user/{encoded_df_file} s3://{bucket}/{encoded_df_file}")


######### Saving Content #########
# Save original dataframe with all of the process column being true. 
content_df["to_encode"] = False # Set entire process column to False.
content_lake_dict = content_df.to_dict(orient='records')
logging.debug(f"Length of Concatenated Dictionary: {len(content_lake_dict)}")

with open(f'/home/ec2-user/content-lake.json', 'w') as file:
    json.dump(content_lake_dict, file, indent=4)

logging.info("Inserting content back to s3 after finishing encoding process.")
os.system(f"aws s3 cp /home/ec2-user/content-lake.json s3://toast-daily-content/content-lake.json")


######### Exiting Script #########
logging.info("Encoding Proces Finished Exiting Instance:")
instance_id = "i-061dff9fc11bb2250"
os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')