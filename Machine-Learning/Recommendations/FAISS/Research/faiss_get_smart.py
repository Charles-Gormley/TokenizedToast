# Indexing
# Flat Index: IndexFlatL2. This is the simplest index type which doesn't use any compression (quantization). It's basically a brute-force search. While exact, it's not memory efficient for very large datasets.

# IVF Index: This type partitions the dataset into a number of clusters (like k-means). At search time, it only compares the query to the vectors in a few clusters, which accelerates the search. However, it's an approximation method, so it may not always return the exact nearest neighbors.

# PQ Index: This uses product quantization to compress vectors. While it reduces the memory footprint significantly, it's also an approximation method.

# Hybrid Index: Combines IVF and PQ for both clustering and compression benefits.



import faiss
import numpy as np

# Generating some data
d = 64                                 # dimension
nb = 100000                            # database size
nq = 10000                             # nb of queries
np.random.seed(1234)
xb = np.random.random((nb, d)).astype('float32')
xb[:, 0] += np.arange(nb) / 1000.
xq = np.random.random((nq, d)).astype('float32')
xq[:, 0] += np.arange(nq) / 1000.

# Building an index
index = faiss.IndexFlatL2(d)
print(index.is_trained)
index.add(xb)
print(index.ntotal)

k = 5
D, I = index.search(xq, k)
print("Neighbor's Indices")
print(I[0])  # Neighbors for the first 
print("Distances")
print(D[0])  # Corresponding distances

# Create an IVF index
nlist = 100
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_L2)

# Train the index
assert not index.is_trained
index.train(xb)
assert index.is_trained
index.add(xb)

# Search
D, I = index.search(xq, k)
print("Neighbors of 5 Q")
print(I[0])  # Neighbors for the first 5 queries
print("Distances")
print(D[0])  # Corresponding distances
