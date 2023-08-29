from pymilvus import Collection, Milvus, DataType, CollectionSchema, FieldSchema, connections
import torch
import numpy as np

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StartMilvus:
    def __init__(self, collection_name:str, embeddings_path:str):
        self.collection_name = collection_name # 'BERT_Encodings'
        self.embeddings_path = embeddings_path # '/home/ec2-user/embeddings.pth'

    def load_encodings(self):
        logging.info("Loading Encodings locally")
        db = torch.load(self.embeddings_path)
        tensors = db['tensor']
        encodings_list = [tensor.cpu().numpy() for tensor in tensors]
        self.vectors = np.vstack(encodings_list).tolist()

        ids = db['ID']
        ids_list = [tensor.cpu().numpy() for tensor in ids]
        id_vectors = np.vstack(ids_list).tolist()
        self.id_vectors = [item for sublist in id_vectors for item in sublist]

        assert len(self.id_vectors) == len(self.vectors), "Lengths of IDs and vectors do not match!"

    def connect_milvus(self):
        logging.info("Starting milvus instance")
        # Initialize a Milvus instance
        connections.connect(host='localhost', port='19530')  # Change these as needed

    def create_schema(self):
        logging.info("Initializing Schmea")
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

        self.schema = CollectionSchema(fields=fields, description="BERT Encodings for News Articles")
            
    def create_collection(self):
        self.collection = Collection(self.collection_name, schema=self.schema)

    def insert_collection(self):
        logging.info("Inserting Data")
        insert_data = [self.id_vectors, self.vectors]
        self.collection.insert(insert_data)
        logging.info("Flushing Data")
        self.collection.flush()

        index = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        self.collection.create_index("embedding", index)

    def query_database(self, query_vector):
        # TODO: Assign Type to Query Vector
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(anns_field="embedding", 
                                    data = query_vector, 
                                    param = search_params, 
                                    limit=5, 
                                    output_fields=["id"])
        
        return results

    