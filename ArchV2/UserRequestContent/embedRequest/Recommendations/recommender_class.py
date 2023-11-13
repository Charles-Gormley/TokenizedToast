import faiss
import numpy as np

class Recommendations():
    def __init__(self, vector_embedding="BERT", indexing_technique:str="FlatL2", distance_measurement:str="L2"):
        # Embedding model choice
        self.vector_embedding = vector_embedding
        # Check if the embedding model selected is supported
        if self.vector_embedding not in ["BERT", "Word2Vec", "FastText"]:
            raise ValueError("Unsupported embedding type. Choose from 'BERT', 'Word2Vec', or 'FastText'.")
        
        # Indexing technique choice
        self.indexing_technique = indexing_technique
        # Create a placeholder for the index, which will be created later based on the chosen technique
        self.index = None

        # Distance measurement choice
        self.distance_measurement = distance_measurement
        # Validate the chosen distance measurement
        if self.distance_measurement not in ["L2", "InnerProduct"]: #TODO: Add Canberra, Bray-Curtis, Manhattan, Kullback-Leibler divergence
            raise ValueError("Unsupported distance measurement. Choose 'L2' or 'InnerProduct'.")
        
        dim = self._get_embedding_dim()
        
        if self.indexing_technique == "FlatL2":
            self.index = faiss.IndexFlatL2(dim)
        elif self.indexing_technique == "FlatIP":
            self.index = faiss.IndexFlatIP(dim)
        elif self.indexing_technique == "IVFFlat":
            quantizer = faiss.IndexFlatL2(dim)  # the other index
            self.index = faiss.IndexIVFFlat(quantizer, dim, 10)  # 10 is nlist: number of clusters
        elif self.indexing_technique == "IVFPQ":
            quantizer = faiss.IndexFlatL2(dim)
            self.index = faiss.IndexIVFPQ(quantizer, dim, 10, 8, 8)  # 10 is nlist, 8 is the bits per sub-vector
        elif self.indexing_technique == "PQ":
            self.index = faiss.IndexPQ(dim, 8, 8)  # 8 is the bits per sub-vector
        elif self.indexing_technique == "HNSW":
            self.index = faiss.IndexHNSWFlat(dim, 32)  # 32 is the maximum number of outgoing links in the HNSW graph
        elif self.indexing_technique == "OPQ":
            self.index = faiss.IndexOPQ(dim, 8, 8)  # 8 is the bits per sub-vector
        #TODO: Add in clustering techniques which could be trained on subtopics of data.

        self.set_search_data = False


    def _get_embedding_dim(self):
        # This method returns the embedding dimension based on the chosen embedding type.
        # Note: This is a placeholder. In a real-world scenario, you'd probably fetch this dynamically or have predefined constants.
        if self.vector_embedding == "BERT":
            self.embedding_dim = 768
            return 768
        elif self.vector_embedding == "Word2Vec":
            self.embedding_dim = 300
            return 300
        elif self.vector_embedding == "FastText":
            self.embedding_dim = 300
            return 300
        else:
            raise ValueError("Unsupported embedding type.")
        
    def check_trained(self) -> bool:
        return self.index.is_trained
    
    def train_index(self, training_data:np.array, search_data:np.array, index_data:np.array=None):
        self.index.train(training_data)
        self.index.add_with_ids(search_data, index_data)

    def add_vectors_to_index(self, search_data:np.array):
        """Add data vectors to the FAISS index."""
        self.search_data = search_data   
        self.set_search_data = True     
        self.index.add(search_data)

    def get_ids(self):
        return self.index.id_map

    def create_test_data(self, num_samples=1000):
        """Generate synthetic test data and add it to the FAISS index."""
        test_data = np.random.uniform(low=-2, high=2, size=(num_samples, self.embedding_dim)).astype('float32')
        
        if not self.set_search_data:
            self.add_vectors_to_index(test_data)
        return test_data

    def search(self, input:np.array, k=None):
        """Search using the predefined input and k."""
        self.input = input
        if k:
            self.k = k

        if len(self.input.shape) == 1:  # Check if input is a 1D array
            query = self.input.reshape(1, -1)
        else:
            query = self.input
            
        distances, indices = self.index.search(query, self.k)
        return distances, indices
    

    def eliminate_duplicate_vectors(self, threshold=0.0000000001):
        """Eliminate vectors with duplicate or near similar embeddings."""
        
        # List to keep track of vectors to keep
        unique_vectors = []
        unique_indices = []
        
        for _, vec in enumerate(self.search_data):
            distances, indices = self.index.search(vec.reshape(1, -1), 2)  # Searching for the two closest neighbors (itself and the next closest one)
            
            # If the second closest vector (i.e., the closest one other than the vector itself) has a distance greater than the threshold, 
            # it means it's unique. Else, it's a duplicate or near similar.
            if distances[0][1] > threshold:
                unique_vectors.append(vec)
        
        # Replace self.input with the unique vectors
        self.search_data = np.array(unique_vectors, dtype='float64')
        
        # Update the index with only the unique vectors
        self.index.reset()  # Clear the current index
        self.add_vectors_to_index(self.search_data)


def test_recommender(vector_embedding="BERT", 
                     indexing_technique:str="FlatL2", 
                     distance_measurement:str="L2",
                     batch=5):
    
    '''This function lives outside of the class. Test to make sure the function works'''
    
    # Assuming you have a Recommender class
    recommender = Recommendations(vector_embedding, indexing_technique, distance_measurement)
    
    # Generate some test data, for example, 1000 vectors of dimension 768 for BERT embeddings
    test_data = np.random.random((1000, 768)).astype('float32')
    recommender.add_vectors_to_index(test_data)
    
    # Generate some query vectors, for example, 5 vectors of dimension 768
    query_vectors = np.random.random((batch, 768)).astype('float32')
    
    # Perform searches for each query vector
    for q_vec in query_vectors:
        distances, indices = recommender.search(q_vec, 4)
        
        # Basic assertions to check if everything is functioning
        assert distances.shape[1] == recommender.k
        assert indices.shape[1] == recommender.k
        
    
    
    distances, indices = recommender.search(query_vectors, 5)
    assert distances.shape[0] == batch
    assert indices.shape[0] == batch