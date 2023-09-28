import sparknlp
from sparknlp.pretrained import PretrainedPipeline
from sparknlp.base import *
from sparknlp.annotator import *
from pyspark.ml import Pipeline

import pandas
import torch



spark = sparknlp.start()

print("Spark NLP version: {}".format(sparknlp.version()))
print("Apache Spark version: {}".format(spark.version))

# PIPELINE CREATION
clean_pipeline = PretrainedPipeline('clean_stop', lang = 'en')
ner_pipeline = PretrainedPipeline('onto_recognize_entities_bert_large', lang = 'en') # Name Entity Recognition
finsen_pipeline = PretrainedPipeline("classifierdl_bertwiki_finance_sentiment_pipeline", "en")

# Ingest the Data From S3



ner_annot = ner_pipeline.fullAnnotate(data)[0]
clean_annot = clean_pipeline.fullAnnotate(data)[0]
finsen_annot = finsen_pipeline.fullAnnotate(data)[0]

# Output Key Specific data for each article to respective S3 buckets with specific article ids.

