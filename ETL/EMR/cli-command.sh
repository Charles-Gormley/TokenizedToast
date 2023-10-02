#!/bin/bash

aws emr create-cluster \
--name "Spark NLP 5.1.2" \
--release-label emr-6.2.0 \
--applications Name=Hadoop Name=Spark Name=Hive \
--instance-type m4.4xlarge \
--instance-count 3 \
--use-default-roles \
--log-uri "s3://spark-nlp-logs/" \
--bootstrap-actions Path=s3://toast-scripts/emr-bootstrap.sh \
--configurations "https://spark-nlp-configs.s3.amazonaws.com/software-config.json" \
--ec2-attributes KeyName=key-0403d3df15144f1bb,EmrManagedMasterSecurityGroup=sg-0dbdf53296082ef59,EmrManagedSlaveSecurityGroup=sg-009393133ee9572da \
--profile default