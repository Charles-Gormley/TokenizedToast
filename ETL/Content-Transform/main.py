from cleaning import Cleaner
import pickle
from datetime import datetime
now = datetime.now()
m = str(now.month)
d = str(now.day)
y = str(now.year)
cleaned_data_fn = 'cleaned-data.pkl'
content_json_fn = 'content.json'

content_json_path = "/home/ec2-user/" + content_json_fn
cleaner = Cleaner(content_json_path)
df = cleaner.clean_data()


with open(cleaned_data_fn, 'wb') as f:
    pickle.dump(df, f)