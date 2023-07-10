import hdbscan
from hdbscan.prediction import approximate_predict
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

import os
import pickle

def open_umappings(umap_path:str):
    with open(umap_path, 'rb') as f:
        umap_encodings = pickle.load(f)

    return umap_encodings

# ######### Training Methods #########
def train_hdbscan(model_dict:dict,
                  encodings:np.ndarray,
                  min_cluster_size:int,
                  cluster_selection_epsilon:int,
                  cluster_selection_method:str,
                  alpha:float,
                  metric:str
                  ):

    model = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, 
                            cluster_selection_epsilon=cluster_selection_epsilon,
                            cluster_selection_method=cluster_selection_method,
                            alpha=alpha,
                            metric=metric,
                            prediction_data=True
                            )

    model.fit(encodings) # Insert np.ndarray here.

    model_dict.update(model.get_params())
    return model, model_dict



def train_kmeans(model_dict: dict, 
                 encodings: np.ndarray, 
                 n_clusters: int, 
                 init: str='k-means++', 
                 n_init: int=10, 
                 max_iter: int=300, 
                 tol: float=1e-4):
    
    model = KMeans(n_clusters=n_clusters, 
                   init=init, 
                   n_init=n_init, 
                   max_iter=max_iter, 
                   tol=tol, 
                   random_state=42)

    model.fit(encodings)

    # Add model parameters to the dictionary
    model_dict.update(model.get_params())
    return model, model_dict

# ######### Evaluation Methods #########
def silhouette(model_dict:dict,
               encodings:np.ndarray,
               model):
    labels = model.labels_

    if len(set(labels)) > 1:
        silhouette_avg = silhouette_score(encodings, labels)
        model_dict['silhoutte_score'] = silhouette_avg
        return model_dict

def calinski_harabasz(model_dict: dict, encodings: np.ndarray, model):
    labels = model.labels_

    if len(set(labels)) > 1:  # Ensure there's more than one cluster
        calinski_harabasz_avg = calinski_harabasz_score(encodings, labels)
        model_dict['calinski_harabasz_score'] = calinski_harabasz_avg
        return model_dict

def davies_bouldin(model_dict: dict, encodings: np.ndarray, model):
    labels = model.labels_

    if len(set(labels)) > 1:  # Ensure there's more than one cluster
        davies_bouldin_avg = davies_bouldin_score(encodings, labels)
        model_dict['davies_bouldin_score'] = davies_bouldin_avg
        return model_dict


