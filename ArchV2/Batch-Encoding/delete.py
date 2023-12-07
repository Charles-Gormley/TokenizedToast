import os
import json
import logging
import pandas as pd
import numpy as np
import torch

from datetime import datetime, timedelta
bucket = "toast-encodings"
encoded_df_file = "encoded_df.feather"
embeddings_file = 'embeddings.pth'

os.system(f"aws s3 cp s3://toast-daily-content/content-lake.json /home/ec2-user/content-lake.json")
with open(f'/home/ec2-user/content-lake.json', 'r') as file:
    old_content_lake = json.load(file)

encoded_df = pd.DataFrame(old_content_lake)
encoded_df['to_encode'] = True


new_encoded_tensor = np.array(encoded_df['tensor'].apply(lambda tensor: tensor.squeeze(0)))
new_article_id_time = torch.tensor(encoded_df['unixTime'].values)
new_article_id_tensor = torch.tensor(encoded_df['articleID'].values)

embeddings = encoded_df['tensor'].apply(lambda tensor: tensor.squeeze(0)).values
concatenated_embeddings = {
    'articleID': torch.tensor(encoded_df['articleID'].values),
    'tensor': embeddings,
    'unixTime': torch.tensor(encoded_df['unixTime'].values)
}
torch.save(concatenated_embeddings, f"/home/ec2-user/{embeddings_file}")
os.system(f"aws s3 cp /home/ec2-user/{embeddings_file} s3://{bucket}/{embeddings_file}")

encoded_df["to_encode"] = False
content_lake_dict = encoded_df.to_dict(orient='records')
logging.debug(f"Length of Concatenated Dictionary: {len(content_lake_dict)}")
with open(f'/home/ec2-user/content-lake.json', 'w') as file:
    json.dump(content_lake_dict, file, indent=4)

logging.info("Inserting content back to s3 after finishing encoding process.")
os.system(f"aws s3 cp /home/ec2-user/content-lake.json s3://toast-daily-content/content-lake.json")
