aws emr create-cluster \
--name "Spark NLP 5.1.2" \
--release-label emr-6.2.0 \
--applications Name=Hadoop Name=Spark Name=Hive \
--instance-type m4.4xlarge \
--instance-count 3 \
--use-default-roles \
--log-uri "s3://<S3_BUCKET>/" \
--bootstrap-actions Path=s3://<S3_BUCKET>/emr-bootstrap.sh,Name=custome \
--configurations "https://<public_access>/sparknlp-config.json" \
--ec2-attributes KeyName=<your_ssh_key>,EmrManagedMasterSecurityGroup=<security_group_with_ssh>,EmrManagedSlaveSecurityGroup=<security_group_with_ssh> \
--profile <aws_profile_credentials>