from recommender_class import Recommendations
from load_content import ProcessContent

recommender = Recommendations()

# Load in data from BERT embeddings
content = ProcessContent()
content.load_df()
content.load_tensors()
search_data, index_data = content.load_encodings()


print(index_data.shape)
print(search_data.shape)
print(type(index_data))

# Check if BERT embeddings are valid
recommender.add_vectors_to_index(search_data)
recommender.eliminate_duplicate_vectors()

# TODO: Create new drop duplicates function. 

#TODO: Load in data from query BERT Embeddings
query_data = recommender.create_test_data(num_samples=1)
query_data = search_data[0]
#TODO: Check if query BERT embeddings are valid

#TODO: Decide on design of query data. It could have 2 dimensions for each user and a 3rd dimension for every user. Then maybe we could either just iteratively recommend OR 1) Flatten 2) Recommend

distances, seq_indices = recommender.search(query_data, 5)
indices = index_data[seq_indices]

print(distances)
print(indices)
for i in indices[0]:
    print(content.grab_article(i))
