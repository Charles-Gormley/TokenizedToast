import os
import logging
import time

logging.basicConfig(level=logging.INFO)

def run_docker_compose():
    # Change to the /home directory
    os.chdir('/home/ec2-user')

    retries = 10
    success = False

    for i in range(retries):
        logging.info(f'Attempt {i+1} to run docker-compose...')
        exit_code = os.system('sudo docker-compose up -d')
        
        if exit_code == 0:
            success = True
            logging.info('Successfully ran docker-compose.')
            break
        else:
            logging.warning(f'Failed attempt {i+1}. Retrying...')
            time.sleep(5)  # wait for 5 seconds before retrying

    return success

def stop_ec2_instance(instance_id):
    logging.info(f'Stopping EC2 instance {instance_id}...')
    os.system(f'aws ec2 stop-instances --instance-ids {instance_id}')
    logging.info(f'EC2 instance {instance_id} has been stopped.')

def main(instance_id):
    if not run_docker_compose():
        stop_ec2_instance(instance_id)

