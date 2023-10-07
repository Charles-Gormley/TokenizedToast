from aws_tools import save_to_s3, link_lambda

# Upload new emr script to emr bucket

path_to_lambda = '/home/ec2-user/TokenizedToast/Lambdas/'
lambda_bucket = 'toast-lambdas'

etl_file = 'MidnightPusher.py'
ml_file = 'StartEncodingJob.py'
failsafe_file = 'Failsafe-EC2-Costs.py'

save_to_s3('toast-scripts', path_to_lambda+etl_file, etl_file)
save_to_s3('toast-scripts', path_to_lambda+ml_file, ml_file)
save_to_s3('toast-scripts', path_to_lambda+failsafe_file, failsafe_file)


link_lambda('MidnightPusher', lambda_bucket, etl_file)
link_lambda('StartEncodingJob', lambda_bucket, ml_file)
link_lambda('Failsafe-EC2-Costs', lambda_bucket, failsafe_file)