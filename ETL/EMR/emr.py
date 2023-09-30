import logging
import argparse
import os
from datetime import datetime
import pickle


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

cleaned_data_fn_date = f'cleaned-data{todays_str}.pkl'
cleaned_data_fn = 'cleaned-data.pkl'
s3_annotation_url = f"s3://toast-daily-analytics/{todays_str}"


# Load Pretrained Pipelines
def load_model(s3_location):
    return PretrainedPipeline.from_disk(s3_location)

# clean_pipeline = load_model('s3://spark-nlp-models/clean_stop_en_3.0.0_3.0_1616544492033/')
# ner_pipeline = load_model()
finsen_pipeline = load_model('s3://spark-nlp-models/classifierdl_bertwiki_finance_sentiment_pipeline_en_4.3.0_3.0_1673543221872/')

# # Loading in DataFrame
# def load_dataset(s3_path):
#     local_path = "/tmp/df.pkl"
#     os.system(f"aws s3 cp {s3_path} {local_path}")
#     df = spark.read.csv(local_path, header=True, inferSchema=True)
#     return df

# # # Ingest Data from S3 or create a test dataframe
# if not testing:
#     logging.info("Ingesting Data from S3...")
#     df = load_dataset(f"s3://toast-daily-content/{cleaned_data_fn}")
# else:
#     logging.info("Creating a test dataframe...")
#     data = {'index': [1, 2], 'link': ['http://example.com/1', 'http://example.com/2'], 'title': ['Title1', 'Title2'],
#             'content': ['''Test 1 2 3 ''', '''Testing 1 2 3'''], 'date': ['2023-01-01', '2023-01-02']}
#     df = pd.DataFrame(data)

# # Transformations
# logging.info("Creating and transforming dataframes...")
# df = spark.createDataFrame(df)
# df = df.withColumnRenamed("content", "text")

# # df = clean_pipeline.transform(df)
# # df = ner_pipeline.transform(df)
# annotations = finsen_pipeline.transform(df)

# logging.info("Writing annotations to parquet...")
# annotations.write.parquet(s3_annotation_url)

# logging.info("Script completed.")
