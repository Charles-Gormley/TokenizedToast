import pickle
import json
import os

os.chdir("C:/Users/Charl/Documents/Projects/TokenizedToast/ETL/RSS-Extractor")

# Load the list from the pickle file
with open('rss-feeds.pkl', 'rb') as f:
    data = pickle.load(f)

print(type(data))

# Convert the list to JSON
json_data = json.dumps(data)

# Write the JSON data to a file
with open('rss-feeds.json', 'w') as f:
    f.write(json_data)



import json

# Load the JSON data from the file
with open('rss-feeds.json', 'r') as f:
    json_data = json.load(f)

print(json_data[10])

