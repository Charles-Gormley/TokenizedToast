from aws_tools import upload_to_lambda

# Upload new emr script to emr bucket

path_to_lambda = '/home/ec2-user/TokenizedToast/Lambdas/'
bucket = 'toast-lambdas'

etl = 'MidnightPusher'
mle = 'StartEncodingJob'
fls = 'Failsafe-EC2-Costs'

upload_to_lambda(path_to_lambda+etl+'.py', etl, bucket)
upload_to_lambda(path_to_lambda+mle+'.py', mle, bucket)
upload_to_lambda(path_to_lambda+fls+'.py', fls, bucket)