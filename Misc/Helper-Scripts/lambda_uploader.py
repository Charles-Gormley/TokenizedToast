from aws_tools import save_to_s3, link_lambda, zip_files, copy_files_lambda

# Upload new emr script to emr bucket

path_to_lambda = '/home/ec2-user/TokenizedToast/Lambdas/'
lambda_bucket = 'toast-lambdas'

etl_file = 'MidnightPusher.py'
ml_file = 'StartEncodingJob.py'
failsafe_file = 'Failsafe-EC2-Costs.py'

lambda_file = 'lambda_function.py'

copy_files_lambda(path_to_lambda+etl_file, 'MidnightPusher')
copy_files_lambda(path_to_lambda+ml_file, 'StartEncodingJob')
copy_files_lambda(path_to_lambda+failsafe_file, 'Failsafe-EC2-Costs')

# Temporarily zip python files
zip_files(f'MidnightPusher/{lambda_file}', '/tmp/output-etl.zip')
zip_files(f'StartEncodingJob/{lambda_file}', '/tmp/output-ml.zip')
zip_files(f'Failsafe-EC2-Costs/{lambda_file}', '/tmp/output-failsafe.zip')

save_to_s3(lambda_bucket, '/tmp/output-etl.zip', 'output-etl.zip')
save_to_s3(lambda_bucket, '/tmp/output-ml.zip', 'output-ml.zip')
save_to_s3(lambda_bucket, '/tmp/output-failsafe.zip', 'output-failsafe.zip')

link_lambda('MidnightPusher', lambda_bucket, 'output-etl.zip')
link_lambda('StartEncodingJob', lambda_bucket, 'output-ml.zip')
link_lambda('Failsafe-EC2-Costs', lambda_bucket, 'output-failsafe.zip')