from encodingclasses import BERT

import os
import pickle
import random
from tqdm import tqdm

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

wikipedia_corpus_path = 'D:/INFO323/TokenizedToast/corpus-all.pkl'

def save_pickle(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)

logging.info("Loading Wikipedia Corpus")
if os.path.exists(wikipedia_corpus_path):
    with open(wikipedia_corpus_path, 'rb') as file:
        corpus = pickle.load(file)

encoder = BERT()
batch_size = 1000  # Adjust the batch size as per your available memory

num_articles = len(corpus)
num_batches = (num_articles + batch_size - 1) // batch_size

logging.info("Encoding and Saving Corpus in Batches")
for batch_idx in tqdm(range(num_batches)):
    start_idx = batch_idx * batch_size
    end_idx = min((batch_idx + 1) * batch_size, num_articles)
    batch_corpus = corpus[start_idx:end_idx]

    # Encode the batch
    encodings = encoder.encode_corpus(batch_corpus)

    # Perform UMAP embedding if needed
    umap_encodings = encoder.umap_embeddings(encodings)

    # Save the UMAP encodings as a pickle file
    pickle_filename = f'umaps_wikipedia_batch{batch_idx}.pkl'
    save_pickle(umap_encodings, pickle_filename)

logging.info("All Batches Processed")