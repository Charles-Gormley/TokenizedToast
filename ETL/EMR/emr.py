import logging
import argparse
from datetime import datetime


from pyspark.sql import SparkSession
import sparknlp
import joblib
from sparknlp.pretrained import PretrainedPipeline
from sparknlp.base import *
from sparknlp.annotator import *
import pandas as pd
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') # Setting Log Levels

# Testing Levels
testing = False


################### SETUP #########################
logging.info("Starting PySpark")
spark = SparkSession.builder \
    .appName("Spark NLP") \
    .master("yarn") \
    .config("spark.driver.memory", "16G") \
    .config("spark.driver.maxResultSize", "16G") \
    .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:3.3.1").config("spark.kryoserializer.buffer.max", "2000M") \
    .getOrCreate()
spark = sparknlp.start()


# Declaring File Names
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

clean_pipeline =load_model()
ner_pipeline = load_model()
finsen_pipeline = load_model('s3://spark-nlp-models/classifierdl_bertwiki_finance_sentiment_pipeline_en_4.3.0_3.0_1673543221872/')

# # Ingest Data from S3 or create a test dataframe
# if not testing:
#     logging.info("Ingesting Data from S3...")
#     df = spark.read.csv(f"s3://toast-daily-content/{cleaned_data_fn}")
# else:
#     logging.info("Creating a test dataframe...")
#     data = {'index': [1, 2], 'link': ['http://example.com/1', 'http://example.com/2'], 'title': ['Title1', 'Title2'],
#             'content': ['''Test 1 2 3 ''', '''Testing 1 2 3'''], 'date': ['2023-01-01', '2023-01-02']}
#     df = pd.DataFrame(data)

# # Transformations
# logging.info("Creating and transforming dataframes...")
# df = spark.createDataFrame(df)
# df = df.withColumnRenamed("content", "text")

# df = clean_pipeline.transform(df)
# df = ner_pipeline.transform(df)
# annotations = finsen_pipeline.transform(df)

# logging.info("Writing annotations to parquet...")
# annotations.write.parquet(s3_annotation_url)

# logging.info("Script completed.")
