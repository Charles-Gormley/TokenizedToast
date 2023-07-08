from encodings import BERT

import os
import pickle

wikipedia_corpus_path = 'D:/INFO323/TokenizedToast/corpus-all.pkl'

if os.path.exists(wikipedia_corpus_path):
    with open(wikipedia_corpus_path, 'rb') as file:
        corpus = pickle.load(file)

encoder = BERT()

encodings = encoder.encode_corpus(corpus)

umap_encodings = encoder.umap_embeddings(encodings)

# Save np.ndarray as a pickel file
with open('umaps_wikipedia.pkl', 'wb') as f:
    pickle.dump(umap_encodings, f)