import logging
import argparse
import os
from datetime import datetime
import pickle
from io import BytesIO

import boto3
from pyspark.sql import SparkSession
from pyspark import SparkConf
import sparknlp
import joblib
from sparknlp.pretrained import PretrainedPipeline
from sparknlp.base import *
from sparknlp.annotator import *
import pandas as pd
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Setting Log Levels

# Testing Levels
testing = False

import sparknlp
from sparknlp.pretrained import PretrainedPipeline

# create or get Spark Session

spark = sparknlp.start()

print(sparknlp.version())
print(spark.version)

pipeline = PretrainedPipeline('recognize_entities_dl', 'en')
result = pipeline.annotate('The Mona Lisa is a 16th century oil painting created by Leonardo')


################### SETUP #########################
# Set up Spark configuration
conf = SparkConf()

conf.set("spark.master", "yarn")
conf.set("spark.driver.memory", "16g")
conf.set("spark.executor.memory", "16g")
conf.set("spark.driver.cores", "8")
conf.set("spark.executor.cores", "8")
conf.set("spark.driver.memoryOverhead", "2048")
conf.set("spark.executor.memoryOverhead", "2048")
conf.set("spark.kryoserializer.buffer.max", "2000M")
conf.set("spark.pyspark.python", "/usr/bin/python3")
conf.set("spark.pyspark.driver.python", "/usr/bin/python3")

logging.info("Starting PySpark")
spark = SparkSession.builder \
    .appName("Spark NLP") \
    .config(conf=conf) \
    .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:5.1.2") \
    .getOrCreate()

sparknlp.start()

logging.info("Versioning")
print("Spark NLP version: {}".format(sparknlp.version()))
print("Apache Spark version: {}".format(spark.version))

# Declaring File Names

logging.info("Setting Data time File Names")
now = datetime.now()
m = str(now.month)
d = str(now.day)
y = str(now.year)
todays_str = f'{y}-{m}-{d}'

cleaned_data_fn = 'cleaned-data.csv'
output_file = 'annotations.json'
s3_annotation_url = f"s3://toast-daily-analytics/{todays_str}/{output_file}"


# Load Pretrained Pipelines

logging.info("Loading Pretrained Pipelines")
def load_model(s3_location):
    logging.info("Loading Model From S3 ")
    return PretrainedPipeline.from_disk(s3_location)

finsen_pipeline = load_model('s3://spark-nlp-models/classifierdl_bertwiki_finance_sentiment_pipeline_en_4.3.0_3.0_1673543221872/') # Financial Sentiment Analysis

# Retry Logic
max_retries, tries = 5, 0 
while tries < max_retries:
    try:
        ner_pipeline = PretrainedPipeline('onto_recognize_entities_bert_medium', lang = 'en') # Name Entity Recognition
        tries = max_retries
    except:
        logging.info(f"Retrying{str(tries)}")
        tries += 1
        pass


# Loading in DataFrame
logging.info("Loading in s3 Client")
s3client = boto3.client('s3')
def load_dataset(bucket:str, key:str, s3client=s3client):
    logging.info("Loading in file")
    # response = s3client.get_object(Bucket=bucket, Key=key)
    csv_path = f"s3://{bucket}/{key}"
    df = spark.read.csv(csv_path, header=True, inferSchema=True)
    return df

# # Ingest Data from S3 or create a test dataframe
if not testing:
    logging.info("Production Environment")
    logging.info("Ingesting Data from S3...")
    df = load_dataset("toast-daily-content", cleaned_data_fn)
else:
    logging.info("Creating a test dataframe...")
    data = {'index': [1, 2], 'link': ['http://example.com/1', 'http://example.com/2'], 'title': ['Title1', 'Title2'],
            'content': ['''Test 1 2 3 ''', '''Testing 1 2 3'''], 'date': ['2023-01-01', '2023-01-02']}
    df = pd.DataFrame(data)

# Transformations
logging.info("Column Rename...")
df = df.withColumnRenamed("content", "text")

# logging.info("Clean Pipeline Transformation")
# df = clean_pipeline.transform(df)

logging.info("Name Entity Recognition Pipeline")
df = finsen_pipeline.transform(df)
df = ner_pipeline.transform(df)

logging.info("Outputting Df columns")
print(df.columns)

logging.info("Changing column names")
df = df.drop(*'date','checked', 'sentence_embeddings', 'ner', 'document', 'sentence', 'text', 'token', 'embeddings', "_c0")
print(df.columns)

logging.info("Writing annotations to parquet...")
json_str = df.toJSON().collect()
# Join the list into a single string
json_str = str(json_str)

# Now you can encode the string
json_str = json_str.encode('utf-8')
s3client.put_object(Bucket='toast-daily-analytics', 
                             Key=f'{todays_str}/{output_file}', 
                             Body=json_str,
                             ContentType='application/json', 
                             ContentEncoding='utf-8'
                             )

logging.info("Script completed.")