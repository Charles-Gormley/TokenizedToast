import torch
import os
import pandas as pd
import json
import subprocess
from encoder import encode_dataframe_column, load_df
import logging

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(processName)s] [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

from datetime import datetime
now = datetime.now()


# Load in the content lake from s3 as pandas dataframe.
os.system(f"aws s3 cp s3://toast-daily-content/content-lake.json /home/ec2-user/content-lake.json")
with open(f'/home/ec2-user/content-lake.json', 'r') as file:
    old_content_lake = json.load(file)
    
    df = pd.DataFrame(old_content_lake)
    logging.debug(f"Old Dataframe Content Lake Head: {df.head()}")
    logging.debug(f"Length of old dataframe: {len(df)}")


# TODO: Split dataframe into one that only has data that needs to processed
process_df = df[df["to_encode"] == True]
encoded_df = encode_dataframe_column(process_df, "content")

# Load in older dataframe

# Concatenate dataframe.


logging.info("Starting encoding dataframe column")
encoded_df = encode_dataframe_column(df, "content")
encoded_df['tensor'] = encoded_df['tensor'].apply(lambda tensor: tensor.squeeze(0))
logging.info("Length of Encoder Tensors: %d", len(encoded_df['tensor']))

logging.info("Saving encoded file")
id_tensor = torch.tensor(encoded_df['id'].values)
encoded_tensor = encoded_df['tensor'].values

torch.save({'ID':id_tensor, 'tensor':encoded_tensor}, embeddings_file)

encoded_df = encoded_df.drop('tensor', axis=1)
logging.info("Saving encoded DataFrame to file")
# Save DataFrame to file
encoded_df.to_feather(encoded_df_file)

logging.info("Saving Encodings to S3")
save_to_s3("encoder-milvus-bucket", encoded_df_file, encoded_df_file)
save_to_s3("encoder-milvus-bucket", embeddings_file, embeddings_file)

logging.info("Running the Recommendation System")
os.system('python3.9 /home/ec2-user/TokenizedToast/Machine-Learning/Recommendations/main.py')

logging.info(f"Deleting {cleaned_data_fn} from drive to save on storage")
os.system(f"rm {cleaned_data_fn}")

logging.info("Stopping Encoding | Milvus Instance")

# Section: Shutting off instance
logging.info("Process Finished Shuting off ec2 instance")
stop_ec2_instance("i-061dff9fc11bb2250")


# TODO: Make sure the git update is working 
