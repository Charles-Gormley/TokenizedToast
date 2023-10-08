#!/bin/bash

CONFIG_JSON=$(curl -s "https://spark-nlp-configs.s3.amazonaws.com/software-config.json")
STEPS='[{"Name":"emr","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Args":["spark-submit","--deploy-mode","cluster","--master","yarn","s3://toast-scripts/emr.py"],"Type":"CUSTOM_JAR"}]'

aws emr create-cluster \
--name "Spark NLP 5.1.2" \
--release-label emr-6.10.0 \
--applications Name=Hadoop Name=Spark Name=Hive \
--managed-scaling-policy '{"ComputeLimits":{"UnitType":"Instances","MinimumCapacityUnits":2,"MaximumCapacityUnits":20,"MaximumOnDemandCapacityUnits":20,"MaximumCoreCapacityUnits":20}}' \
--instance-type m4.2xlarge \
--instance-count 3 \
--log-uri "s3://spark-nlp-logs/" \
--bootstrap-actions Path=s3://toast-scripts/emr_boostrap.sh \
--configurations "$CONFIG_JSON" \
--ec2-attributes KeyName=Spark-NLP-Key-Pair,EmrManagedMasterSecurityGroup=sg-0dbdf53296082ef59,EmrManagedSlaveSecurityGroup=sg-009393133ee9572da,SubnetId=subnet-0085a33ae13b3d5e3 \
--steps "$STEPS" \
--use-default-roles \
--profile default \
--scale-down-behavior "TERMINATE_AT_TASK_COMPLETION" \
--auto-terminate \
--region "us-east-1"