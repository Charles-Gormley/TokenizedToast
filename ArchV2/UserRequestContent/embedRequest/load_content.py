import pandas as pd
import numpy as np
import torch

import logging
from datetime import datetime
import boto3
import io

s3_client = boto3.client('s3')


class ProcessContent:
        def __init__(self):
            pass

        def load_df(self):
            now = datetime.now()
            m = now.month
            d = now.day
            y = now.year
            key = f'cleaned-data{y}-{m}-{d}.pkl'
            bucket = 'toast-daily-content'
            
            # Loading in pandas dataframe
            response = s3_client.get_object(Bucket=bucket, Key=key)
            file_content = response['Body'].read()
            self.df = pd.read_pickle(io.BytesIO(file_content))

            # Cleaning dataframe
            self.df.drop_duplicates(subset="content", inplace=True)
            self.df.dropna(how="all", inplace=True)


        def grab_article(self, query_index:int) -> str:
            
            content_value = self.df[self.df["index"] == query_index]
            return content_value
        
        def load_tensors(self, embeddings_path='/home/ec2-user/embeddings.pth'):
            logging.info("Loading Encodings locally")
            self.db = torch.load(embeddings_path)

        def load_encodings(self, embeddings_path ='/home/ec2-user/embeddings.pth'):
            self.load_df()
            self.load_tensors()

            
            tensors = self.db['tensor']
            encodings_list = [tensor.cpu().numpy() for tensor in tensors]
            self.vectors = np.vstack(encodings_list)

            ids = self.db['ID']
            ids_list = [tensor.cpu().numpy() for tensor in ids]
            id_vectors = np.vstack(ids_list).tolist()
            self.id_vectors = [item for sublist in id_vectors for item in sublist]
            self.id_vectors = np.array(self.id_vectors)

            assert len(self.id_vectors) == len(self.vectors), "Lengths of IDs and vectors do not match!"
            assert len(self.id_vectors) == len(self.df["index"]), "Index length of content dataframe & encodings do not match! ID Length: " + str(len(self.id_vectors)) + \
                " Index DF Length: " + str(len(self.df["index"]))
            return self.vectors, self.id_vectors
            