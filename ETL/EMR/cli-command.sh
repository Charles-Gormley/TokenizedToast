#!/bin/bash

CONFIG_JSON=$(curl -s "https://spark-nlp-configs.s3.amazonaws.com/software-config.json")
STEPS='[{"Name":"emr","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Args":["spark-submit","--deploy-mode","cluster","--master","yarn","s3://toast-scripts/emr.py"],"Type":"CUSTOM_JAR"}]'

aws emr create-cluster \
--name "Spark NLP 5.1.2" \
--release-label emr-6.2.0 \
--applications Name=Hadoop Name=Spark Name=Hive \
--service-role "arn:aws:iam::966265353179:role/EMR_DefaultRole" \
--managed-scaling-policy '{"ComputeLimits":{"UnitType":"Instances","MinimumCapacityUnits":2,"MaximumCapacityUnits":20,"MaximumOnDemandCapacityUnits":20,"MaximumCoreCapacityUnits":20}}' \
--instance-type m4.4xlarge \
--instance-count 3 \
--log-uri "s3://spark-nlp-logs/" \
--bootstrap-actions Path=s3://toast-scripts/emr_boostrap.sh \
--configurations "$CONFIG_JSON" \
--ec2-attributes KeyName=Spark-NLP-Key-Pair,EmrManagedMasterSecurityGroup=sg-0dbdf53296082ef59,EmrManagedSlaveSecurityGroup=sg-009393133ee9572da,SubnetId=subnet-0085a33ae13b3d5e3 \
--steps "$STEPS" \
--profile default \
 --scale-down-behavior "TERMINATE_AT_TASK_COMPLETION" \
 --auto-termination-policy '{"IdleTimeout":3600}' \
--region "us-east-1"


# aws emr create-cluster \
#  --name "ETL-Toast" \
#  --log-uri "s3n://aws-logs-966265353179-us-east-1/elasticmapreduce/" \
#  --release-label "emr-6.10.0" \
#  --service-role "arn:aws:iam::966265353179:role/EMR_DefaultRole" \
#  --managed-scaling-policy '{"ComputeLimits":{"UnitType":"Instances","MinimumCapacityUnits":2,"MaximumCapacityUnits":20,"MaximumOnDemandCapacityUnits":20,"MaximumCoreCapacityUnits":20}}' \
#  --ec2-attributes '{"InstanceProfile":"AmazonEMR-InstanceProfile-20230930T095730","EmrManagedMasterSecurityGroup":"sg-0dbdf53296082ef59","EmrManagedSlaveSecurityGroup":"sg-009393133ee9572da","AdditionalMasterSecurityGroups":[],"AdditionalSlaveSecurityGroups":[],"SubnetId":"subnet-0085a33ae13b3d5e3"}' \
#  --applications Name=Spark Name=Zeppelin \
#  --instance-groups '[{"InstanceCount":1,"InstanceGroupType":"TASK","Name":"Task - 1","InstanceType":"m5.8xlarge","EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"VolumeType":"gp2","SizeInGB":128},"VolumesPerInstance":4}],"EbsOptimized":true}},{"InstanceCount":1,"InstanceGroupType":"MASTER","Name":"Primary","InstanceType":"m5.8xlarge","EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"VolumeType":"gp2","SizeInGB":32},"VolumesPerInstance":2}],"EbsOptimized":true}},{"InstanceCount":1,"InstanceGroupType":"CORE","Name":"Core","InstanceType":"m5.xlarge","EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"VolumeType":"gp2","SizeInGB":32},"VolumesPerInstance":2}],"EbsOptimized":true}}]' \
#  --bootstrap-actions '[{"Args":[],"Name":"emr_bootstrap","Path":"s3://toast-scripts/emr_boostrap.sh"}]' \
#  --steps '[{"Name":"emr","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Args":["spark-submit","--deploy-mode","cluster","--master","yarn","s3://toast-scripts/emr.py"],"Type":"CUSTOM_JAR"},{"Name":"emr","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Args":["spark-submit","--deploy-mode","cluster","--master","yarn","s3://toast-scripts/emr.py"],"Type":"CUSTOM_JAR"},{"Name":"emr","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Args":["spark-submit","--deploy-mode","cluster","--master","yarn","s3://toast-scripts/emr.py"],"Type":"CUSTOM_JAR"},{"Name":"emr","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Args":["spark-submit","--deploy-mode","cluster","--master","yarn","s3://toast-scripts/emr.py"],"Type":"CUSTOM_JAR"},{"Name":"emr","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Args":["spark-submit","--deploy-mode","cluster","--master","yarn","s3://toast-scripts/emr.py"],"Type":"CUSTOM_JAR"},{"Name":"emr","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Args":["spark-submit","--deploy-mode","cluster","--master","yarn","s3://toast-scripts/emr.py"],"Type":"CUSTOM_JAR"}]' \
#  --scale-down-behavior "TERMINATE_AT_TASK_COMPLETION" \
#  --auto-termination-policy '{"IdleTimeout":3600}' \
#  --os-release-label "2.0.20230808.0" \
#  --region "us-east-1"