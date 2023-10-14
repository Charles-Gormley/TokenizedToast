from recommender_class import Recommendations
from load_content import ProcessContent

from sys import path
path.append("/home/ec2-user/TokenizedToast/User")
from user_events import UserStructure
u = UserStructure()

recommender = Recommendations()

# Load in data from BERT embeddings
content = ProcessContent()
search_data, index_data = content.load_encodings()


# Check if BERT embeddings are valid
recommender.add_vectors_to_index(search_data)
recommender.eliminate_duplicate_vectors()

# TODO: Create new drop duplicates function. 
users = u.load_users_From_s3()
print(users)
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
