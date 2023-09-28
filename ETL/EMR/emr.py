
import sparknlp
from sparknlp.pretrained import PretrainedPipeline
from sparknlp.base import *
from sparknlp.annotator import *
from pyspark.ml import Pipeline


spark = sparknlp.start()

print("Spark NLP version: {}".format(sparknlp.version()))
print("Apache Spark version: {}".format(spark.version))

# Initialize all the pipelines - NER, BERT, FINBERT
pipeline_n_base = PretrainedPipeline('onto_recognize_entities_bert_medium', lang = 'en')
# NER embeddings
ner_pipeline = PretrainedPipeline('onto_recognize_entities_bert_medium', lang = 'en')

# Financial BERT embeddings
documentAssembler = DocumentAssembler() \
.setInputCol("text") \
.setOutputCol("document")

tokenizer = Tokenizer() \
.setInputCols("document") \
.setOutputCol("token")

embeddings = BertEmbeddings.pretrained("bert_embeddings_sec_bert_base","en") \
.setInputCols(["document", "token"]) \
.setOutputCol("embeddings")

finbert_pipeline = Pipeline(stages=[documentAssembler, tokenizer, embeddings])

# Normal BERT Embeddings
documentAssembler = DocumentAssembler() \
.setInputCol("text") \
.setOutputCol("document")

tokenizer = Tokenizer() \
.setInputCols("document") \
.setOutputCol("token")

embeddings = RoBertaEmbeddings.pretrained("roberta_embeddings_distilroberta_base","en") \
.setInputCols(["document", "token"]) \
.setOutputCol("embeddings")

bert_pipeline = Pipeline(stages=[documentAssembler, tokenizer, embeddings])


# Ingest the Data From S3

# Set the data as test data.
data = spark.createDataFrame([[test_data]]).toDF("text")

ner_annot = ner_pipeline.fullAnnotate(test_data)[0]
bert_annot = bert_pipeline.fit(data).transform(data)
finbert_annot = finbert_pipeline.fit(data).transform(data)

# Output Key Specific data for each article to respective S3 buckets with specific article ids.

