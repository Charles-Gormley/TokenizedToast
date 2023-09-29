import logging
from pyspark.ml import Pipeline
import pandas as pd
import torch
from datetime import datetime
import sparknlp
from sparknlp.pretrained import PretrainedPipeline
from sparknlp.base import *
from sparknlp.annotator import *
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Script started.")

# Print versions
logging.info(f"Spark NLP version: {sparknlp.version()}")
spark = sparknlp.start()
logging.info(f"Apache Spark version: {spark.version}")

# Generate date string for today
now = datetime.now()
m = str(now.month)
d = str(now.day)
y = str(now.year)
todays_str = f'{y}-{m}-{d}'

cleaned_data_fn_date = f'cleaned-data{todays_str}.pkl'
cleaned_data_fn = 'cleaned-data.pkl'

# File Paths
s3_annotation_url = f"s3://toast-daily-analytics/{todays_str}"

# Initialize the argument parser
logging.info("Parsing arguments...")
parser = argparse.ArgumentParser(description="Process some arguments.")
parser.add_argument("--testing", type=bool, default=False, help="Number of the article. Default is False.")
args = parser.parse_args()
testing = args.testing

# Load Pretrained Pipelines
logging.info("Loading Pretrained Pipelines...")
clean_pipeline = PretrainedPipeline('clean_stop', lang='en')
ner_pipeline = PretrainedPipeline('onto_recognize_entities_bert_large', lang='en')
finsen_pipeline = PretrainedPipeline("classifierdl_bertwiki_finance_sentiment_pipeline", "en")

# Ingest Data from S3 or create a test dataframe
if not testing:
    logging.info("Ingesting Data from S3...")
    df = spark.read.csv(f"s3://toast-daily-content/{cleaned_data_fn}")
else:
    logging.info("Creating a test dataframe...")
    data = {'index': [1, 2], 'link': ['http://example.com/1', 'http://example.com/2'], 'title': ['Title1', 'Title2'],
            'content': ['''Test 1 2 3 ''', '''Testing 1 2 3'''], 'date': ['2023-01-01', '2023-01-02']}
    df = pd.DataFrame(data)

# Transformations
logging.info("Creating and transforming dataframes...")
df = spark.createDataFrame(df)
df = df.withColumnRenamed("content", "text")

df = clean_pipeline.transform(df)
df = ner_pipeline.transform(df)
annotations = finsen_pipeline.transform(df)

logging.info("Writing annotations to parquet...")
annotations.write.parquet(s3_annotation_url)

logging.info("Script completed.")
