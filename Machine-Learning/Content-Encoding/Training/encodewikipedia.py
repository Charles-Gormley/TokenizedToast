from encodingclasses import BERT

import os
import pickle
import random

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

wikipedia_corpus_path = 'D:/INFO323/TokenizedToast/corpus-all.pkl'


logging.info("Loading wikipedia Corpus")
if os.path.exists(wikipedia_corpus_path):
    with open(wikipedia_corpus_path, 'rb') as file:
        corpus = pickle.load(file)

encoder = BERT()
logging.info("Encoding Corpus")
encodings = encoder.encode_corpus(corpus)

logging.info("Mapping Encodings")
umap_encodings = encoder.umap_embeddings(encodings)

# Save np.ndarray as a pickel file
with open('umaps_wikipedia.pkl', 'wb') as f:
    pickle.dump(umap_encodings, f)