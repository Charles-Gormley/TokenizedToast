import pandas as pd
import numpy as np
import torch
import logging

class ProcessContent:
        def __init__(self):
            pass

        def load_df(self):
            self.df = pd.read_pickle("/home/ec2-user/cleaned-data.pkl")
            self.df.drop_duplicates(subset="content", inplace=True)
            self.df.dropna(how="all", inplace=True)


        def grab_article(self, query_index:int) -> str:
            print(len(self.df))
            content_value = self.df[self.df["index"] == query_index]
            return content_value
        
        def load_tensors(self, embeddings_path='/home/ec2-user/embeddings.pth'):
            logging.info("Loading Encodings locally")
            self.db = torch.load(embeddings_path)

        def load_encodings(self, embeddings_path ='/home/ec2-user/embeddings.pth'):
            tensors = self.db['tensor']
            encodings_list = [tensor.cpu().numpy() for tensor in tensors]
            self.vectors = np.vstack(encodings_list)

            ids = self.db['ID']
            ids_list = [tensor.cpu().numpy() for tensor in ids]
            id_vectors = np.vstack(ids_list).tolist()
            self.id_vectors = [item for sublist in id_vectors for item in sublist]
            self.id_vectors = np.array(self.id_vectors)

            assert len(self.id_vectors) == len(self.vectors), "Lengths of IDs and vectors do not match!"
            assert len(self.id_vectors) == len(self.df["index"]), "Index length of content dataframe & encodings do not match! ID Length: " + str(self.id_vectors) + \
                " Index DF Length: " + str(self.df["index"])
            return self.vectors, self.id_vectors
            