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


article_ids = []

def calculate_requests(length:float, format:str, num_topics:int):
    '''length: minutes'''

    reading_wpm = 300 # Newsletter. 
    talking_wpm = 200 # Podcast - Based on popular ted talks 

    target_sum_time = 30 # 30 seconds per summary of an article.
    requests = ((length/num_topics)*60)/target_sum_time

    if format == "Newsletter":
        target_word_count = reading_wpm / target_sum_time

    else:
        target_word_count - talking_wpm / target_sum_time

    return requests, target_word_count
    
def load_content_from_s3():
    '''This is going to hold the data for past 3 days of article encodings. In the future this is going to run on zillis. '''
    # TODO: Implement this batch S3 bucket in my batch processing ec2 instance.
    

def embedUserTopics(event):
    basicTopics = event['basicTopics']
    advancedTopics = event['advancedTopics']
    userId = event['userId']
    length = event['length']
    format = event['format']

    topics = basicTopics + advancedTopics
    requests, target_word_count = calculate_requests(length, format, num_topics=len(topics))
    
    encodings = []

    # Iterate over basicTopics & advancedTopics
    for topic in topics:
        # Get Recommendations 

        encoding = encode_single_article(topic, tokenizer, model)
        encodings.append(encoding)

        # TODO For each encoding grab the recommendations
        cur_ids = recommendation(encodings, content_store, requests)
        article_ids.append(cur_ids)
        
    for id in article_ids:
        # Grab the articles content from dynamo db.

    

def lambda_handler(event, context):

    # Convert to JSON string
    return {
        'statusCode': 200,
        'body': json.dumps(encodings)
    }
