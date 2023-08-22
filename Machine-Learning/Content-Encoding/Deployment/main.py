import os
import encoder
import logging

log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

def download_from_s3(bucket, key, destination):
    logging.info(f"Starting download from s3://{bucket}/{key} to {destination}")
    command = f'aws s3 cp s3://{bucket}/{key} {destination}'
    os.system(command)
    logging.info(f"Finished download from s3://{bucket}/{key} to {destination}")

# Example usage
bucket_name = 'toast-daily-content'
file_key = 'cleaned-data.pkl'
destination_path = 'cleaned-data.pkl'



if os.getcwd() == "C:\Users\Charl\Documents\Projects\TokenizedToast":
    print("In local computer")
    df_path = 'cleaned-data.pkl'

else:
    download_from_s3(bucket_name, file_key, destination_path)
    df_path = 'cleaned-data.pkl'
    

logging.info("Loading dataframe from pickle file")
df = encoder.load_df(df_path)

logging.info("Starting encoding dataframe column")
encoded_df = encoder.encode_dataframe_column(df, "content")

logging.info("Saving encoded DataFrame to file")
# Save DataFrame to file
encoded_df.to_pickle("encoded_df.pkl")
