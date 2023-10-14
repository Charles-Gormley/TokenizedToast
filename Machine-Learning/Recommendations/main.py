from recommender_class import Recommendations
from load_content import ProcessContent

from torch import stack, save, load

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
queries = []

for user in users:
    if not user['new']: # Basically if it is an old user with embeddings saved.
        # Get the email
        # Get the Name
        query = dict()
        info = u.load_user_info(user['name'], user['user_id'])
        logging.info(f"Loading in embeddings for {user['user_id']}-{user['name']}")
        system(f"aws s3 cp s3://toast-users/{user['user_id']}-{user['name']}/embeddings.pt combined_topic_embeddings.pt ")

        query['name'] = user['name']
        query['email'] = info['Email']
        query['pref'] = info['Summarization preferences']
        query['embeddings'] = load('combined_topic_embeddings.pt')
        queries.append(query)
        
        

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
        # Get the embedding vector, the name and email of the user.

        # Getting query data:
        query = dict()
        info = u.load_user_info(user['name'], user['user_id'])
        query['name'] = user['name']
        query['email'] = info['Email']
        query['pref'] = info['Summarization preferences']
        query['embeddings'] = combined_tensor
        queries.append(query)
        
    u.update_users_json(users)



logging.info('Initializing Content Process class and load in bert embeddings.')
content = ProcessContent() 
search_data, index_data = content.load_encodings()



logging("Adding vectors to recommendation class")
recommender = Recommendations # Initializing Recommender Class
recommender.add_vectors_to_index(search_data) # Check if BERT embeddings are valid
recommender.eliminate_duplicate_vectors() # Eliminating any other duplicate articles with vector similarity

query_data = recommender.create_test_data(num_samples=1)
query_data = search_data[0]


for query in queries:
    distances, seq_indices = recommender.search(query['embeddings'], 2)
    indices = index_data[seq_indices]
    query['articles'] = []
    
    for i in indices[0]:
        a = content.grab_article(i)
        print(a)
        query['articles'].append(a)
    # Send to Lambda with (Email, Preferences, Name, Articles)