import os
import logging



def start_ec2_instance(instance_id):
    os.system(f'aws ec2 start-instances --instance-ids {instance_id}')

def stop_ec2_instance(instance_id):
    os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')

def save_to_s3(bucket_name, file_path, s3_key):
    os.system(f'aws s3 cp {file_path} s3://{bucket_name}/{s3_key}')

def download_from_s3(bucket, key, destination):
    logging.info(f"Starting download from s3://{bucket}/{key} to {destination}")
    command = f'aws s3 cp s3://{bucket}/{key} {destination}'
    os.system(command)
    logging.info(f"Finished download from s3://{bucket}/{key} to {destination}")

def link_lambda(lambda_function:str, bucket:str, key:str):
    os.system(f'aws lambda update-function-code --function-name {lambda_function} --s3-bucket {bucket} --s3-key {key}')

