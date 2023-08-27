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
userprojects_table = client_dynamo.Table("UserProjects")


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
        # Updating in the user projects table
        print(update_user_projects(userid, projectid))

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
        # Updating in the user projects table
        print(remove_user_project(userid, projectid))

    except ClientError as err:
        print("Failed to delete chats", err)


def check_project_limits(userid):
    response = userprojects_table.get_item(Key={'UserId': userid})
    item = response.get('Item', {})
    proj_count = item.get('ProjectCount', 0)
    print(proj_count)
    if proj_count >= 5:
        return False
    return False


def update_user_projects(userid, project_id):
    response = userprojects_table.update_item(
        Key={'UserId': userid},
        UpdateExpression='SET ProjectCount = if_not_exists(ProjectCount, :zero) + :incr, ProjectIds = list_append(if_not_exists(ProjectIds, :empty_list), :project_id)',
        ExpressionAttributeValues={
            ':zero': 0,
            ':incr': 1,
            ':empty_list': [],
            ':project_id': [project_id]
        },
        ReturnValues='UPDATED_NEW'
    )
    return response


def remove_user_project(userid, project_id):
    response = userprojects_table.get_item(Key={'UserId': userid})
    item = response.get('Item', {})

    if 'ProjectIds' in item:
        project_ids = item['ProjectIds']
        project_ids.remove(project_id)

        response = userprojects_table.update_item(
            Key={'UserId': userid},
            UpdateExpression='SET ProjectCount = ProjectCount - :decr, ProjectIds = :proj_ids',
            ExpressionAttributeValues={
                ':decr': 1,
                ':proj_ids': project_ids
            },
            ReturnValues='UPDATED_NEW'
        )

        return response
    else:
        return None


def fetch_user_projects(userid):
    response = userprojects_table.get_item(Key={'UserId': userid})
    item = response.get('Item', {})

    if 'ProjectIds' in item:
        return item['ProjectIds']
    else:
        return []
