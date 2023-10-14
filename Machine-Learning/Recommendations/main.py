from recommender_class import Recommendations
from load_content import ProcessContent

from torch import stack, save

from os import system
from sys import path
import logging
logging.basicConfig(level=logging.INFO)


logging.info("Loading in User encoding library")
path.append("/home/ec2-user/TokenizedToast/Machine-Learning/User-Encoding")
from encoder import encode_single_article

logging.info("Loading in the user events library")
path.append("/home/ec2-user/TokenizedToast/User")
from user_events import UserStructure
u = UserStructure()

users = u.load_users_from_s3()
for user in users:
    if user['new'] and u.check_s3_interest(user['name'], user['user_id']):
        logging.info(f"Converting {user['user_id']}-{user['name']} to a new user")
        user['new'] = False
        interests = u.load_user_interest(user['name'], user['user_id'])
        topics = interests['topics']
        
        # Embed Topics with BERT
        tensor_list = list()
        for topic in topics:
            tensor = encode_single_article(topic)
            tensor_list.append(tensor)

        combined_tensor = stack(tensor_list) # Stack tensor to mulitple 3 dimensions

        save(combined_tensor, 'combined_topic_embeddings.pt') # Torch function

        # Save BERT Embeddings to users.
        logging.info(f"Saving embeddings for {user['user_id']}-{user['name']}")
        system(f"aws s3 cp combined_topic_embeddings.pt s3://toast-users/{user['user_id']}-{user['name']}/embeddings.pt")        
        
    u.update_users_json(users)
        

recommender = Recommendations()

# Load in data from BERT embeddings
content = ProcessContent()
search_data, index_data = content.load_encodings()


# Check if BERT embeddings are valid
recommender.add_vectors_to_index(search_data)
recommender.eliminate_duplicate_vectors()

# TODO: Create new drop duplicates function. 

# Check if each of the users have user embeddings

#TODO: Load in data from query BERT Embeddings


query_data = recommender.create_test_data(num_samples=1)
query_data = search_data[0]
#TODO: Check if query BERT embeddings are valid

#TODO: Decide on design of query data. It could have 2 dimensions for each user and a 3rd dimension for every user. Then maybe we could either just iteratively recommend OR 1) Flatten 2) Recommend

# Grab Query Data .json with emails, list of encodings, user's summarization preferences. 
# For each encoding obtain an article recommendation. 
# For each recommendation send it to the GPT Summarizer 

distances, seq_indices = recommender.search(query_data, 5)
indices = index_data[seq_indices]


for i in indices[0]:
    print(content.grab_article(i))
