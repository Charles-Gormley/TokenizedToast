import torch
import pandas as pd
from transformers import BertTokenizer, BertModel
import logging

from tqdm import tqdm
from joblib import Parallel, delayed

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(processName)s] [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Load pre-trained model tokenizer
cache_dir = "/home/ec2-user/model_cache/"
tokenizer = BertTokenizer.from_pretrained(f"{cache_dir}tokenizer/")
model = BertModel.from_pretrained(f"{cache_dir}model/")
model.eval()

def encode_and_pool(text):
    logging.debug("Starting encoding and pooling")
    # Tokenize the text
    marked_text = "[CLS] " + text + " [SEP]"
    tokenized_text = tokenizer.tokenize(marked_text)
    
    # If the text is too long, chunk it into sequences of up to 512 tokens
    max_length = 512
    if len(tokenized_text) > max_length:
        tokenized_text_chunks = [tokenized_text[i:i + max_length] for i in range(0, len(tokenized_text), max_length)]
    else:
        tokenized_text_chunks = [tokenized_text]

    pooled_outputs = []
    
    for tokenized_text in tokenized_text_chunks:
        indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
        segments_ids = [1] * len(tokenized_text)

        # Convert inputs to PyTorch tensors
        tokens_tensor = torch.tensor([indexed_tokens])
        segments_tensors = torch.tensor([segments_ids])

        # Put tensors on GPU
        tokens_tensor = tokens_tensor.to('cpu')
        segments_tensors = segments_tensors.to('cpu')
        model.to('cpu')

        # Predict hidden states features for each layer
        with torch.no_grad():
            outputs = model(tokens_tensor, segments_tensors)

        
        # Use the embeddings from the last layer
        last_layer = outputs[0]

        # Mean pool the token embeddings to get a single vector for the chunk
        mean_pooled = torch.mean(last_layer, dim=1)
        pooled_outputs.append(mean_pooled)
    
    # Mean pool the chunk embeddings to get a single vector for the text
    pooled_output = torch.mean(torch.stack(pooled_outputs), dim=0)
    logging.debug("Finished encoding and pooling")
    
    return pooled_output


# Assuming the 'encode_and_pool' function is defined elsewhere
def process_row(row, column_name):
    return {
        "text": row[column_name],
        "tensor": encode_and_pool(row[column_name]),
        "articleID": row["articleID"],
        "unixTime": row["unixTime"]
    }

def encode_dataframe_column(dataframe:pd.DataFrame, column_name:str) -> pd.DataFrame:
    logging.info(f"Starting encoding dataframe column '{column_name}'")
    
    # Check if the column exists in the dataframe
    if column_name not in dataframe.columns:
        logging.error(f"The column '{column_name}' is not in the dataframe.")
        return None
    
    # Create a new dataframe with a unique id
    dataframe_with_id = dataframe.reset_index()

    # Use joblib's Parallel and delayed functions to parallelize the computation
    num_cores = -1  # This will use all available cores. Adjust if needed.
    encoded_list = Parallel(n_jobs=num_cores)(delayed(process_row)(row, column_name) for _, row in tqdm(dataframe_with_id.iterrows(), total=dataframe_with_id.shape[0]))
    # Convert list of dictionaries to DataFrame
    encoded_df = pd.DataFrame(encoded_list)

    logging.info(f"Finished encoding dataframe column '{column_name}'")
    
    return encoded_df