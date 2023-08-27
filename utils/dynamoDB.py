import boto3
import json
import os
from dotenv.main import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]

client_dynamo = boto3.resource('dynamodb',
                               aws_access_key_id=AWS_ACCESS_KEY,
                               aws_secret_access_key=AWS_SECRET_KEY,
                               region_name='us-east-1')

table = client_dynamo.Table('users-crito')
chathist_table = client_dynamo.Table("ChatHistory")


def get_UserId(email_id):
    # get the user details for the old email
    # retrieve the user record from the database
    response = table.query(
        KeyConditionExpression='email_id = :email_id',
        ExpressionAttributeValues={
            ':email_id': email_id
        }
    )
    # print("dynamo db",response)
    if 'Items' not in response or len(response['Items']) == 0:
        # return an error message if the old email doesn't exist
        return 'Email does not exist'
    user_id = response['Items'][0]['user_id']
    return user_id


def store_user_chats(userid, projectid, query, resp):

    chat_entry = {
        'Query': query,
        'Response': resp
    }
    print(chat_entry)
    try:
        update_expression = "SET chats = list_append(if_not_exists(chats, :empty_list), :chat_entry)"
        expression_values = {
            ':empty_list': [],
            ':chat_entry': [chat_entry]
        }

        chathist_table.update_item(
            Key={'UserId': userid, 'ProjectId': projectid},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        print("Chat updated successfully")

    except ClientError as err:
        print("Failed to Update chatHistroy", err)


def fetch_user_chats(userid, projectid):
    try:
        response = chathist_table.get_item(
            Key={'UserId': userid, 'ProjectId': projectid}
        )
        item = response.get('Item', {})
        chat_history = item.get('chats', [])
        print(chat_history)
        return chat_history
    except ClientError as err:
        print("Failed to retrieve chat history", err)
        return []


def delete_user_chats(userid, projectid):
    try:
        chathist_table.delete_item(
            Key={'UserId': userid, 'ProjectId': projectid}
        )
        print("Chats deleted successfully")

    except ClientError as err:
        print("Failed to delete chats", err)


# This is only once to create the table chat History table

# import boto3

# dynamodb =boto3.resource('dynamodb',
#                             aws_access_key_id=AWS_ACCESS_KEY,
#                             aws_secret_access_key=AWS_SECRET_KEY,
#                             region_name='us-east-1')

# table_name = 'ChatHistory'  # Replace this with your desired table name

# # Define the attribute definitions for the table
# attribute_definitions = [
#     {'AttributeName': 'UserId', 'AttributeType': 'S'},
#     {'AttributeName': 'SortKey', 'AttributeType': 'S'}
# ]

# # Define the primary key schema
# key_schema = [
#     {'AttributeName': 'UserId', 'KeyType': 'HASH'},    # Partition key
#     {'AttributeName': 'SortKey', 'KeyType': 'RANGE'}   # Sort key
# ]

# # Define the provisioned throughput (adjust as needed)
# provisioned_throughput = {
#     'ReadCapacityUnits': 5,   # Adjust as needed
#     'WriteCapacityUnits': 5   # Adjust as needed
# }

# # Create the DynamoDB table
# response = dynamodb.create_table(
#     TableName=table_name,
#     AttributeDefinitions=attribute_definitions,
#     KeySchema=key_schema,
#     ProvisionedThroughput=provisioned_throughput
# )

# print("Table creation response:", response)
