from cleaning import Cleaner
import pickle
from datetime import datetime
now = datetime.now()
m = str(now.month)
d = str(now.day)
y = str(now.year)
cleaned_data_fn = 'cleaned-data.pkl'
content_json_fn = 'content.json'
cleaned_data_hdf_fn = 'cleaned-data.hdf'

content_json_path = "/home/ec2-user/" + content_json_fn
cleaned_data_path = "/home/ec2-user/" + cleaned_data_fn
cleaned_data_hdf_path = "/home/ec2-user/" + cleaned_data_hdf_fn

cleaner = Cleaner(content_json_path)
df = cleaner.clean_data()


with open(cleaned_data_path, 'wb') as f:
    pickle.dump(df, f)


with open(cleaned_data_hdf_path, 'wb') as f:
    pickle.HIGHEST_PROTOCOL = 4
    df.to_hdf(cleaned_data_hdf_path, 'df')