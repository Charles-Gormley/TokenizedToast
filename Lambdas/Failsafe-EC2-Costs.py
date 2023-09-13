import json
import boto3

# Create EC2 client
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Define the instance ID you want to stop
    encoding_id = 'i-061dff9fc11bb2250'
    puller_id = 'i-0ea95298232d8ed99'
    instance_ids = [encoding_id, puller_id]
    
    try:
        response = ec2.stop_instances(InstanceIds=instance_ids)
        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully initiated stop for instances: {instance_ids}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error stopping instances: {str(e)}')
        }