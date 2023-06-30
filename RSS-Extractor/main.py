import queue
import threading
import pickle
import json
from tqdm import tqdm


with open('rss-feeds.pkl', 'rb') as f:
    feeds = pickle.load(f) # Single list of feeds
print(len(feeds))


content_archive = []
for i in tqdm(range(len(feeds)), total=len(feeds)):
    
    output = feeds[i]

    output_queue = queue.Queue()
    thread = threading.Thread(target=extract_feed, args=(output, output_queue,))
    try:
        thread.start()
        thread.join(timeout=20)
        if thread.is_alive():
            thread.terminate()
            thread.join()
            
        else:
            output = output_queue.get()
    except:
        pass
    
    content_archive.append(output)

from datetime import datetime

for i in content_archive:
    for j in i['articles']:
        if j == {}:
            continue
        elif j['date'] == None:
            j['date'] = 'None'
        else:
            date_str = j['date'].strftime("%Y-%m-%d")
            j['date'] = date_str

json_data = json.dumps(content_archive)

with open('content.json', 'w') as json_file:
    json_file.write(json_data)

