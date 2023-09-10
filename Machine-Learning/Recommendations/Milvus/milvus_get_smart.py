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

id_vectors = [item for sublist in id_vectors for item in sublist]
assert len(id_vectors) == len(vectors), "Lengths of IDs and vectors do not match!"

collection = Collection(collection_name, schema=schema)


# Insert data
logging.info("Inserting Data")
insert_data = [id_vectors, vectors]
collection.insert(insert_data)

# Flush data (makes sure data is written)
collection.flush()

index = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
}
collection.create_index("embedding", index)


# Search in the collection
search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
results = collection.search(anns_field="embedding", 
                            data = vectors[0], 
                            param = search_params, 
                            limit=5, 
                            output_fields=["id"])

