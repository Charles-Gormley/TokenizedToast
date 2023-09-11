from cleaning import Cleaner
import pickle

content_json_path = '/home/ec2-user/content.json'
cleaner = Cleaner(content_json_path)
df = cleaner.clean_data()


with open('cleaned-data.pkl', 'wb') as f:
    pickle.dump(df, f)