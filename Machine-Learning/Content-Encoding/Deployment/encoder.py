import torch
import pandas as pd
from transformers import BertTokenizer, BertModel
import logging

logging.basicConfig(level=logging.INFO)

# Load pre-trained model tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Load pre-trained model
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()

def load_df(df_path):
    return pd.read_pickle(df_path)

def encode_and_pool(text):
    logging.info("Starting encoding and pooling")
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
    logging.info("Finished encoding and pooling")
    
    return pooled_output

def encode_dataframe_column(dataframe, column_name):
    logging.info(f"Starting encoding dataframe column '{column_name}'")
    # Check if the column exists in the dataframe
    if column_name not in dataframe.columns:
        print(f"The column '{column_name}' is not in the dataframe.")
        return
    
    # Create a new dataframe with a unique id
    dataframe_with_id = dataframe.reset_index()
    encoded_list = dataframe_with_id.apply(lambda row: {"id": row['index'], "text": row[column_name], "tensor": encode_and_pool(row[column_name])}, axis=1)

    # Convert list of dictionaries to DataFrame
    encoded_df = pd.DataFrame.from_records(encoded_list.tolist())

    logging.info(f"Finished encoding dataframe column '{column_name}'")

    return encoded_df

