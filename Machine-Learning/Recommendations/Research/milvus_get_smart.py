# TODO/BUG CHECKLIST:
# - Ensure Milvus server is running and accessible.
# - Validate that PyMilvus client version is compatible with the Milvus server version.
# - Validate that `id_vectors` are all integers and of equal length with `vectors`.
# - Validate that `vectors` are lists of lists with floating-point numbers of the specified dimension.
# - Attempt insertion in smaller batches to isolate potential problematic data.
# - If data seems fine, consider raising the issue with the Milvus community or checking for known issues.



from pymilvus import Collection, Milvus, DataType, CollectionSchema, FieldSchema, connections
import torch
import numpy as np

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Loading Encodings locally")
db = torch.load('/home/ec2-user/embeddings.pth')
tensors = db['tensor']
encodings_list = [tensor.cpu().numpy() for tensor in tensors]
vectors = np.vstack(encodings_list).tolist()

ids = db['ID']
ids_list = [tensor.cpu().numpy() for tensor in ids]
id_vectors = np.vstack(ids_list).tolist()

logging.info("Starting milvus instance")
# Initialize a Milvus instance
connections.connect(host='localhost', port='19530')  # Change these as needed

logging.info("Initializing Schmea")
collection_name = 'BERT_Encodings'
dimension = 768
fields = [
    FieldSchema(name="id",
                dtype=DataType.INT64,
                description="ID",
                is_primary=True),

    FieldSchema(name="embedding", 
                dtype=DataType.FLOAT_VECTOR, 
                dim=dimension, 
                description="vector field", 
                is_primary=False)
    ]

schema = CollectionSchema(fields=fields, description="BERT Encodings for News Articles")

logging.info("Creating Collection")
# existing_collections = connections.list_collections()
# if collection_name in existing_collections:
#     connections.drop_collection(collection_name)

for i in range(len(vectors)):
    for element in vectors[i]:
        if 
        print(type(element))
    if type(vectors[i]) != type(id_vectors[i]):
        print("Yuh")

assert len(id_vectors) == len(vectors), "Lengths of IDs and vectors do not match!"

collection = Collection(collection_name, schema=schema)


# Insert data
ids = collection.insert({"id": id_vectors,"embedding": vectors})

# Flush data (makes sure data is written)
connections.flush([collection_name])

# Search in the collection
search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
results = connections.search(collection_name, [vectors[0]], search_params, limit=5)

# Print the results
for hit in results[0]:
    print(hit.id, hit.distance)
