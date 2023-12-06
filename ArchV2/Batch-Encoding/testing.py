# Download the existing embeddings file from S3
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
content_df["to_encode"] = True

######### Encoding Content #########
# Split dataframe into one that only has data that needs to processed
process_df = content_df[content_df["to_encode"] == True]
if testing:
    process_df = process_df.head()

encoded_df = encode_dataframe_column(process_df, "content") # This needs (article id, data, and encoding.)

os.system(f"aws s3 cp s3://{bucket}/{embeddings_file} /home/ec2-user/{embeddings_file}")
old_embeddings = torch.load(f"/home/ec2-user/{embeddings_file}")
logging.info(f"Old Torch Tensor Size : {old_embeddings.size()}")

# Filter out data older than 7 days
seven_days_ago = datetime.now() - timedelta(days=7)
old_data_filtered = {k: v[old_embeddings['unixTime'] >= seven_days_ago.timestamp()] for k, v in old_embeddings.items()}

new_article_id_time = torch.tensor(encoded_df['unixTime'].values)
new_article_id_tensor = torch.tensor(encoded_df['articleID'].values)
new_encoded_tensor = encoded_df['tensor'].apply(lambda tensor: tensor.squeeze(0)).values

concatenated_embeddings = {
    'articleID': torch.cat([old_data_filtered['articleID'], new_article_id_tensor]),
    'tensor': torch.cat([old_data_filtered['tensor'], new_encoded_tensor]),
    'unixTime': torch.cat([old_data_filtered['unixTime'], new_article_id_time])
}
logging.info("Existing embeddings loaded and concatenated with new embeddings.")
# torch.save(concatenated_embeddings, f"/home/ec2-user/{embeddings_file}")
