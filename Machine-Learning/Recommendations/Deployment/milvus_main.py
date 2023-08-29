import os
import logging
from milvus_functions import StartMilvus
import start_milvus

def main():
    start_milvus.main()
    # Start the Docker-Compose logic
    # I'm assuming the main function from the previous request is available in a module named 'docker_helper'
    # from docker_helper import main as start_docker
    # start_docker()
    
    milvus_instance = StartMilvus(collection_name='BERT_Encodings', embeddings_path='/home/ec2-user/embeddings.pth')
    
    milvus_instance.load_encodings()
    milvus_instance.connect_milvus()
    milvus_instance.create_schema()
    milvus_instance.create_collection()
    milvus_instance.insert_collection()

    # A sample vector for demonstration purposes. Ensure it's 768-dimensional.
    sample_query_vector = [0] * 768 
    results = milvus_instance.query_database(sample_query_vector)
    print(results)

if __name__ == '__main__':
    main()