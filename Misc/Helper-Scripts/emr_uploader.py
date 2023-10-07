from aws_tools import save_to_s3

# Upload new emr script to emr bucket

path_to_emr = '/home/ec2-user/TokenizedToast/ETL/EMR/'
main_emr = 'emr.py'
bootstrap = 'emr_bootstrap.sh'

save_to_s3('toast-scripts', path_to_emr+main_emr, main_emr)
save_to_s3('toast-scripts', path_to_emr+bootstrap, bootstrap)