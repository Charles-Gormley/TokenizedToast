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


######### Saving New Encodings  #########
try: 
    # Download the existing embeddings file from S3
    os.system(f"aws s3 cp s3://{bucket}/{embeddings_file} /home/ec2-user/{embeddings_file}")
    old_embeddings = torch.load(f"/home/ec2-user/{embeddings_file}")

    # Filter out data older than 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    old_data_filtered = {k: v[old_embeddings['unixTime'] >= seven_days_ago.timestamp()] for k, v in old_embeddings.items()}

    new_article_id_time = torch.tensor(encoded_df['unixTime'].values)
    new_article_id_tensor = torch.tensor(encoded_df['articleID'].values)
    new_encoded_tensor = torch.tensor(encoded_df['tensor'].apply(lambda tensor: tensor.squeeze(0)).values)

    concatenated_embeddings = {
        'articleID': torch.cat([old_data_filtered['articleID'], new_article_id_tensor]),
        'tensor': torch.cat([old_data_filtered['tensor'], new_encoded_tensor]),
        'unixTime': torch.cat([old_data_filtered['unixTime'], new_article_id_time])
    }
    logging.info("Existing embeddings loaded and concatenated with new embeddings.")
except Exception as e:
    logging.debug(f"{e}")
    logging.info("First time using embeddings or file not found.")
    concatenated_embeddings = {
        'articleID': torch.tensor(encoded_df['articleID'].values),
        'tensor': torch.tensor(encoded_df['tensor'].apply(lambda tensor: tensor.squeeze(0)).values),
        'unixTime': torch.tensor(encoded_df['unixTime'].values)
    }

torch.save(concatenated_embeddings, f"home/ec2-user/{embeddings_file}")
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


######### Exiting Script #########
logging.info("Encoding Proces Finished Exiting Instance:")
instance_id = "i-061dff9fc11bb2250"
os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')