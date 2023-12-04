import os
import json
import logging
import pandas as pd

from datetime import datetime, timedelta


os.system(f"aws s3 cp s3://toast-daily-content/content-lake.json /home/ec2-user/content-lake.json")
with open(f'/home/ec2-user/content-lake.json', 'r') as file:
    old_content_lake = json.load(file)

df = pd.DataFrame(old_content_lake)
try:
    print(df["to_encode"])
except:
    df["to_encode"] = True # This column does not exists.

logging.debug(f"Old Dataframe Content Lake Head: {df.head()}")
logging.debug(f"Length of old dataframe: {len(df)}")

seven_days_ago = datetime.now() - timedelta(days=7)
logging.debug(f"Length of Concatenated Dataframe: {len(df)}")
content_lake_dict = df.to_dict(orient='records')
logging.debug(f"Length of Concatenated Dictionary: {len(content_lake_dict)}")

with open(f'/home/ec2-user/content-lake.json', 'w') as file:
    json.dump(content_lake_dict, file, indent=4)

logging.info("Inserting content to s3 for content analytics")
os.system(f"aws s3 cp /home/ec2-user/content-lake.json s3://toast-daily-content/content-lake.json")