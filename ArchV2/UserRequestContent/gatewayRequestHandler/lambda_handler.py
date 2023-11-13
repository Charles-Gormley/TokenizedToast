import json
import asyncio
import boto3
from time import time

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    # Setting Varaibles
    time = time()
    userId = event['userId']
    recency = event['recency']
    basicTopics = event['basicTopics']
    advancedTopics = event['advancedTopics']
    tone = event['tone']
    formatType = event['formatType']

    if formatType == "Newsletter":
        length
        opinion
    elif formatType == "Podcast":
        length
        characters
    else:
        logging.error("Invalid Format Type")
    

    async def run_sub_lambdas() -> tuple:
        '''Run all the sub lambdas.'''
        # response = lambda_client.invoke(
        #     FunctionName='other_lambda_function_name',
        #     InvocationType='Event',  # Use 'RequestResponse' for synchronous execution
        #     Payload=json.dumps(payload),
        # )
        pass 

    async def save_user_request_toS3(userId) -> bool:
        pass

    async def get_email() -> str:
        pass

    async def main():
        lambdaTask = asyncio.create_task(run_sub_lambdas())
        s3Task = asyncio.create_task(save_user_request_toS3())
        emailTask = asyncio.create_task(get_email)

        lambdaResults, s3Result, email = await asyncio.gather(lambdaTask, s3Task, emailTask)

        return lambdaResults, s3Result, email
    
    lambdaResults, s3Result, email = asyncio.run(main())


    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
