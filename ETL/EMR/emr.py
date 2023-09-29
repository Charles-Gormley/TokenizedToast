from pyspark.ml import Pipeline

import pandas as pd
import torch
from datetime import datetime


import sparknlp
from sparknlp.pretrained import PretrainedPipeline
from sparknlp.base import *
from sparknlp.annotator import *



print("Spark NLP version: {}".format(sparknlp.version()))
spark = sparknlp.start()

print("Apache Spark version: {}".format(spark.version))

now = datetime.now()
m = str(now.month)
d = str(now.day)
y = str(now.year)
todays_str = f'{y}-{m}-{d}'

cleaned_data_fn_date = f'cleaned-data{todays_str}.pkl' # Doing this for EBS Volume Reasonings
cleaned_data_fn = 'cleaned-data.pkl'

# File Paths
s3_annotation_url = f"s3://toast-daily-analytics/{todays_str}"


import argparse
# Initialize the argument parser
parser = argparse.ArgumentParser(description="Process some arguments.")

# Add the optional argument. If it's not provided, its value will be set to False.
parser.add_argument("--testing", type=bool, default=False,
                    help="Number of the article. Default is False.")
# Parse the provided arguments
args = parser.parse_args()
testing = args.testing





# PIPELINE CREATION
clean_pipeline = PretrainedPipeline('clean_stop', lang = 'en')
ner_pipeline = PretrainedPipeline('onto_recognize_entities_bert_large', lang = 'en') # Name Entity Recognition
finsen_pipeline = PretrainedPipeline("classifierdl_bertwiki_finance_sentiment_pipeline", "en")

# Ingest the Data From S3
if not testing:
    df = spark.read.csv(f"s3://toast-daily-content/{cleaned_data_fn}")

# Test Dataframe
else:
    data = {
        'index': [1, 2],
        'link': ['http://example.com/1', 'http://example.com/2'],
        'title': ['Title1', 'Title2'],
        'content': ['''Test 1 2 3 ''', '''Testing 1 2 3'''],
        'date': ['2023-01-01', '2023-01-02']
    }

    df = pd.DataFrame(data)

# Creating actual dataframe
df = spark.createDataFrame(df)
df = df.withColumnRenamed("content", "text")

df = clean_pipeline.transform(df)
df = ner_pipeline.transform(df)
annotations = finsen_pipeline.transform(df)

annotations.write.parquet(s3_annotation_url)


# TODO: Output analytics dataframes to S3.
# TODO: Add more dates to filenames {cleaned-data.pkl, annotations.parquet, content.json}
# TODO: I guess BERT and the analytics workload can work asynchrounously