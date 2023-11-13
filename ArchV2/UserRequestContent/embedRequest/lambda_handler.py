import os
import json
import boto3

from encoder import encode_single_article

from transformers import BertTokenizer, BertModel

model_dir = './my_model_directory'

tokenizer = BertTokenizer.from_pretrained(model_dir)
model = BertModel.from_pretrained(model_dir)
model.eval()  

s3_client = boto3.client('s3')

def embedUserTopics():
    basicTopics = event['basicTopics']
    advancedTopics = event['advancedTopics']
    userId = event['userId']

    bucket_name = 'your-s3-bucket'

    topics = basicTopics + advancedTopics
    encodings = []

    # Iterate over basicTopics & advancedTopics
    for topic in topics:
        # Get Recommendations 

        encoding = encode_single_article(topic, tokenizer, model)
        encodings.append(encoding)

def lambda_handler(event, context):
    
    
    # Convert to JSON string
    return {
        'statusCode': 200,
        'body': json.dumps(encodings)
    }
