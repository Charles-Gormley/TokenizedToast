import torch
from transformers import BertTokenizer, BertModel
import numpy as np
import umap

import pickle
import os
import random

class BERT:
    def __init__(self):
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        # Initialize tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')

        # Send the model to the GPU
        self.model = self.model.to(self.device)
        
    def bert_encode_overflow(self, article:str) -> torch.Tensor :
        input_ids = self.tokenizer.encode(article, truncation=False)
        chunks = [input_ids[i:i + 512] for i in range(0, len(input_ids), 512)]
        embeddings = []

        for chunk in chunks:
            # Add the required special tokens
            chunk = chunk[:510]  # in case chunk is the last one and has more than 510 tokens
            chunk = [self.tokenizer.cls_token_id] + chunk + [self.tokenizer.sep_token_id]
            
            # Convert to tensor and add batch dimension
            chunk_tensor = torch.tensor(chunk).unsqueeze(0).to(self.device)
            
            # Run through the model
            with torch.no_grad():
                outputs = self.model(chunk_tensor)
                
            # Take the mean of the sequence output (could also use [CLS] token, etc.)
            embedding = outputs.last_hidden_state.mean(dim=1)
            embeddings.append(embedding)

        # Concatenate or average the embeddings from each chunk
        document_embedding = torch.cat(embeddings, dim=0).mean(dim=0)

        return document_embedding
    
    def encode_corpus(self, corpus:list) -> torch.Tensor :
        embeddings = []

        for article in corpus:
            article = article[1] # A text document or article. Article is originally a tuple.
            encoding = self.bert_encode_overflow(article) # Encoding Articles
            

            # Turning BERT Encoding to CPU to save GPU memory.
            encoding = encoding.cpu().numpy()

            # Concatenation of encodings
            embeddings.append(encoding)

        embeddings_tensor = torch.tensor(embeddings)

        return embeddings_tensor

    def umap_embeddings(self, embeddings_tensor: torch.Tensor) -> np.ndarray:
        '''Dimensionality Reduction'''
        array = embeddings_tensor.numpy()

        reduced_embedding = umap.UMAP(n_components=3).fit_transform(array)
        return reduced_embedding

        
