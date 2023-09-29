from cleaning import Cleaner
import pickle
from datetime import date
m = date.month
d = date.day
y = date.year
cleaned_data_fn = f'cleaned-data-{y}-{m}-{d}.pkl'
content_json_fn = f'content-json-{y}-{m}-{d}.json'

content_json_path = f'/home/ec2-user/{content_json_fn}'
cleaner = Cleaner(content_json_path)
df = cleaner.clean_data()


with open(cleaned_data_fn, 'wb') as f:
    pickle.dump(df, f)