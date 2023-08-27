import os
import boto3
from dotenv.main import load_dotenv
from botocore.exceptions import ClientError

final_destination = "Tools/Talk To Docs/"
bucket_name = "crito-ai-primary"

load_dotenv()

AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]


def upload_file_to_s3(filename, file_path, user_id, project_id):
    s3_path = final_destination + user_id + "/" + \
        project_id + "/Training Document/" + filename
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1'
    )

    try:
        s3.upload_file(file_path, bucket_name, s3_path)
        print("File uploaded successfully to S3:", s3_path)
    except Exception as e:
        print("Error uploading file to S3:", str(e))


def delete_file_from_s3(user_id, project_id):
    s3_path = final_destination + user_id + "/" + project_id + "/Training Document/"
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1'
    )
    try:
        s3.delete_object(Bucket=bucket_name, Key=s3_path)
        print("File deleted successfully from S3:", s3_path)
    except ClientError as e:
        print("Error deleting file from S3:", str(e))
