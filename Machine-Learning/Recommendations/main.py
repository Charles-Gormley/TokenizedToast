from recommender_class import Recommendations
from load_content import ProcessContent

from torch import stack, save, load

from os import system
import json
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

users = u.load_users_from_s3() # Loads all of the products users from S3.
queries = []



for user in users:
    if not user['new']: # Basically if it is an old user with embeddings saved.
        ###### Old users ###### 
        
        query = dict()
        info = u.load_user_info(user['name'], user['user_id'])
        logging.info(f"Loading in embeddings for {user['user_id']}-{user['name']}")
        system(f"aws s3 cp s3://toast-users/{user['user_id']}-{user['name']}/embeddings.pt embeddings.pt")
        system(f"aws s3 cp s3://toast-users/{user['user_id']}-{user['name']}/embeddings.pkl embeddings.pkl")

        with open("embeddings.pkl", "rb") as f:
            tensor_list = pickle.load(f)

        query['name'] = user['name'] 
        query['email_address'] = info['Email']
        query['preferences'] = info['Summarization preferences']
        query['embeddings'] = tensor_list 
        # query['embeddings'] = load('embeddings.pt') # This is v1.1. Meaning this is how we are going to parrellize predictions across users.
        
        queries.append(query)
        
        

    if user['new'] and u.check_s3_interest(user['name'], user['user_id']): # This is a new user. This could also apply to users who are having their interests updated.
        ###### New Users ###### 
        logging.info(f"Converting {user['user_id']}-{user['name']} to a new user")
        user['new'] = False # They are now no longer a new user when saved back to S3.
        interests = u.load_user_interest(user['name'], user['user_id'])
        topics = interests['topics']
        
        # Embed Topics with BERT
        tensor_list = list()
        for topic in topics: # Since this is a new user they will need to have their topics encoded. 
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
        query['email_address'] = info['Email']
        query['preferences'] = info['Summarization preferences']
        query['embeddings'] = tensor_list
        # query['embeddings'] = combined_tensor # This is for v1.1

        queries.append(query)
        
    u.update_users_json(users)



logging.info('Initializing Content Process class and load in bert embeddings.')
content = ProcessContent() 
search_data, index_data = content.load_encodings()



logging.info("Adding vectors to recommendation class")
recommender = Recommendations() # Initializing Recommender Class
recommender.add_vectors_to_index(search_data) # Check if BERT embeddings are valid
recommender.eliminate_duplicate_vectors() # Eliminating any other duplicate articles with vector similarity

def send_email_lambda(query:dict):
    lambda_name = "Summarizer-Sender"
    
    query['request_type'] = 'email'
    payload = dict()
    payload = '{'
    vars = ['preferences', 'email_address', 'request_type']
    for var in vars: 
        load = f'"{var}": "{query[var]}",'
        payload = payload + load
    load = f'"articles": {str(query["articles"])}'
    payload = payload + load + "}"
    
    
    system(f"aws lambda invoke --function-name {lambda_name} --payload {payload}")

for query in queries: # Obtained from the above for loop over users.
    query['articles'] = []
    for interest_embedding in query['embeddings']: 
        distances, seq_indices = recommender.search(interest_embedding, 2)
        indices = index_data[seq_indices]
        
        for i in indices[0]:
            a = content.grab_article(i)
            # Index(['index', 'link', 'title', 'content', 'date'], dtype='object')
            # article_tuple = (a['title'].iloc[0], a['content'].iloc[0])
            query['articles'].append(a['content'].iloc[0]) # List of all articles the user would be interested in.
    send_email_lambda(query)
        

    # Send to Lambda with (Email, Preferences, Name, Articles)


