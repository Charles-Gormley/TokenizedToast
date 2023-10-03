#!/bin/bash

CONFIG_JSON=$(curl -s "https://spark-nlp-configs.s3.amazonaws.com/software-config.json")
STEPS='[{"Name":"Main","Type":"Spark","ActionOnFailure":"CONTINUE","Args":["spark-submit","--deploy-mode","client","s3://toast-scripts/emr.py"]}]'

aws emr create-cluster \
--name "Spark NLP 5.1.2" \
--release-label emr-6.2.0 \
--applications Name=Hadoop Name=Spark Name=Hive \
--instance-type m4.4xlarge \
--instance-count 3 \
--use-default-roles \
--log-uri "s3://spark-nlp-logs/" \
--bootstrap-actions Path=s3://toast-scripts/emr_boostrap.sh \
--configurations "$CONFIG_JSON" \
--ec2-attributes KeyName=Spark-NLP-Key-Pair,EmrManagedMasterSecurityGroup=sg-0dbdf53296082ef59,EmrManagedSlaveSecurityGroup=sg-009393133ee9572da \
--steps "$STEPS" \
--profile default