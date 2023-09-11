import torch
import os
from encoder import encode_dataframe_column, load_df
import logging

def start_ec2_instance(instance_id):
    os.system(f'aws ec2 start-instances --instance-ids {instance_id}')

def stop_ec2_instance(instance_id):
    os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')

def save_to_s3(bucket_name, file_path, s3_key):
    os.system(f'aws s3 cp {file_path} s3://{bucket_name}/{s3_key}')

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(processName)s] [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("Changing Directoy command")
os.chdir("/home/ec2-user")
cwd = os.getcwd()
logging.info(f"CWD: {cwd}")

def download_from_s3(bucket, key, destination):
    logging.info(f"Starting download from s3://{bucket}/{key} to {destination}")
    command = f'aws s3 cp s3://{bucket}/{key} {destination}'
    os.system(command)
    logging.info(f"Finished download from s3://{bucket}/{key} to {destination}")

# Example usage
bucket_name = 'toast-daily-content'
file_key = 'cleaned-data.pkl'
destination_path = 'cleaned-data.pkl'
encoded_df_file = "encoded_df.feather"
embeddings_file = 'embeddings.pth'

download_from_s3(bucket_name, file_key, destination_path)

logging.info("Loading dataframe from pickle file")
df = load_df('cleaned-data.pkl')

logging.info("Length of DataFrame Indices: %d", len(df["index"]))

logging.info("Starting encoding dataframe column")
encoded_df = encode_dataframe_column(df, "content")
encoded_df['tensor'] = encoded_df['tensor'].apply(lambda tensor: tensor.squeeze(0))
logging.info("Length of Encoder Tensors: %d", len(encoded_df['tensor']))

logging.info("Saving encoded file")
id_tensor = torch.tensor(encoded_df['id'].values)
encoded_tensor = encoded_df['tensor'].values

torch.save({'ID':id_tensor, 'tensor':encoded_tensor}, embeddings_file)

encoded_df = encoded_df.drop('tensor', axis=1)
logging.info("Saving encoded DataFrame to file")
# Save DataFrame to file
encoded_df.to_feather(encoded_df_file)

logging.info("Saving Encodings to S3")
save_to_s3("encoder-milvus-bucket", encoded_df_file, encoded_df_file)
save_to_s3("encoder-milvus-bucket", embeddings_file, embeddings_file)

logging.info("Stopping Encoding | Milvus Instance")

# Section: Shutting off instance
logging.info("Process Finished Shuting off ec2 instance")
stop_ec2_instance("i-061dff9fc11bb2250")