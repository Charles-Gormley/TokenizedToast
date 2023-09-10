import boto3
import time
import logging

# Instantiate the EC2 and SSM clients here, so they're available to all functions
ec2 = boto3.client('ec2')
ssm = boto3.client('ssm')

def lambda_handler(event, context):
    instance_id = 'i-061dff9fc11bb2250'
    
    main_path = "/home/ec2-user/TokenizedToast/Machine-Learning/Content-Encoding/main.py"
    
    git_command = 'sudo -u ec2-user cd TokenizedToast\nsudo -u ec2-user git fetch\nsudo -u ec2-user git pull'
    main_command = 'sudo -u ec2-user /usr/local/bin/python3.9 ' + main_path + ' >> /tmp/temp.log 2>&1'
    
    # Start the instance
    ec2.start_instances(InstanceIds=[instance_id])

    # Wait a little while to ensure the instance is running
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    
    # Wait for status checks
    wait_for_status_checks(instance_id)
    
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [git_command]}
    )
    time.sleep(10)
    # Send command via SSM
    response = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': [main_command]}
    )

def wait_for_status_checks(instance_id, max_retries=10, sleep_interval=30):
    for _ in range(max_retries):
        response = ec2.describe_instance_status(InstanceIds=[instance_id])
        if response and 'InstanceStatuses' in response:
            status = response['InstanceStatuses'][0]['InstanceStatus']['Status']
            system = response['InstanceStatuses'][0]['SystemStatus']['Status']
            if status == 'ok' and system == 'ok':
                logging.info(f"All status checks passed for instance {instance_id}")
                return
        logging.info(f"Waiting for status checks to complete for instance {instance_id}")
        time.sleep(sleep_interval)
    logging.error(f"Status checks did not complete after {max_retries} retries for instance {instance_id}")