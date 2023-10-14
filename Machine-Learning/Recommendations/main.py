from recommender_class import Recommendations
from load_content import ProcessContent

from torch import stack, save, load

from os import system
from sys import path
import pickle
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
        ###### Old users ###### 
        # Get the email
        # Get the Name
        query = dict()
        info = u.load_user_info(user['name'], user['user_id'])
        logging.info(f"Loading in embeddings for {user['user_id']}-{user['name']}")
        system(f"aws s3 cp s3://toast-users/{user['user_id']}-{user['name']}/embeddings.pt embeddings.pt")
        system(f"aws s3 cp s3://toast-users/{user['user_id']}-{user['name']}/embeddings.pkl embeddings.pkl")

        with open("embeddings.pkl", "rb") as f:
            tensor_list = pickle.load(f)

        query['name'] = user['name']
        query['email'] = info['Email']
        query['pref'] = info['Summarization preferences']
        # query['embeddings'] = load('embeddings.pt') # This is v1.1
        query['embeddings'] = tensor_list 
        queries.append(query)
        
        

    if user['new'] and u.check_s3_interest(user['name'], user['user_id']):
        ###### New Users ###### 
        logging.info(f"Converting {user['user_id']}-{user['name']} to a new user")
        user['new'] = False
        interests = u.load_user_interest(user['name'], user['user_id'])
        topics = interests['topics']
        
        # Embed Topics with BERT
        tensor_list = list()
        for topic in topics:
            tensor = encode_single_article(topic)
            tensor_list.append(tensor)

        with open("embeddings.pkl", "wb") as f:
            pickle.dump(tensor_list, f)

        combined_tensor = stack(tensor_list) # Stack tensor to mulitple 3 dimensions
        save(combined_tensor, 'embeddings.pt') # Torch function

        # Save BERT Embeddings to users.
        logging.info(f"Saving embeddings for {user['user_id']}-{user['name']}")
        system(f"aws s3 cp embeddings.pt s3://toast-users/{user['user_id']}-{user['name']}/embeddings.pt")
        system(f"aws s3 cp embeddings.pkl s3://toast-users/{user['user_id']}-{user['name']}/embeddings.pkl")
        # Get the embedding vector, the name and email of the user.

        # Getting query data:
        query = dict()
        info = u.load_user_info(user['name'], user['user_id'])
        query['name'] = user['name']
        query['email'] = info['Email']
        query['pref'] = info['Summarization preferences']
        # query['embeddings'] = combined_tensor # This is for v1.1
        query['embeddings'] = tensor_list

        queries.append(query)
        
    u.update_users_json(users)



logging.info('Initializing Content Process class and load in bert embeddings.')
content = ProcessContent() 
search_data, index_data = content.load_encodings()



logging.info("Adding vectors to recommendation class")
recommender = Recommendations() # Initializing Recommender Class
recommender.add_vectors_to_index(search_data) # Check if BERT embeddings are valid
recommender.eliminate_duplicate_vectors() # Eliminating any other duplicate articles with vector similarity

query_data = recommender.create_test_data(num_samples=1)
query_data = search_data[0]


for query in queries:
    query['articles'] = []
    for interest_embedding in query['embeddings']: 
        distances, seq_indices = recommender.search(interest_embedding, 2)
        indices = index_data[seq_indices]
        
        for i in indices[0]:
            a = content.grab_article(i)
            print(type(a))
            query['articles'].append(a)
    # Send to Lambda with (Email, Preferences, Name, Articles)

