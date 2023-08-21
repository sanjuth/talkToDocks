import boto3
final_destination="Tools/Talk To Docs/"
bucket_name = "crito-ai-primary"


def upload_file_to_s3(filename, file_path, user_id, project_id ):

    s3_path = final_destination + user_id + "/" + project_id + "/Training Document/" + filename

    AWS_ACCESS_KEY = "AKIAQKDC4DJEJYP4HOSF"
    AWS_SECRET_KEY = "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"
    
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

