import boto3
from botocore.exceptions import ClientError
from dotenv.main import load_dotenv
from botocore.exceptions import ClientError
import os
import json

load_dotenv()

AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]

def get_secret():

    secret_name = "talkToDocs"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print(e)
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)['OPENAI_API_KEY']

