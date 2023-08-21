# import nbformat
# from nbconvert import PythonExporter
import json
import time
import boto3
from io import StringIO
import botocore

from langchain.embeddings.openai import OpenAIEmbeddings


from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import FAISS
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import (
    PyPDFLoader,
    DataFrameLoader,
    GitLoader
  )
import pandas as pd
import os
import openai
import requests
from io import BytesIO
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text

# sqs = boto3.resource('sqs', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')
# sqs_client = boto3.client('sqs', region_name='us-east-1')

s3 = boto3.resource('s3')
bucket = s3.Bucket('crito-ai-primary')

client_dynamo = boto3.resource('dynamodb')
table = client_dynamo.Table('users-crito')
openai.api_key = "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"


def get_text_splits(text_file):
      #Function takes in the text data and returns the splits so for further processing can be done."""
    with open(text_file,'r') as txt:
        data = txt.read()

    textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                                chunk_overlap=15,
                                                length_function=len)
    doc_list = textSplit.split_text(data)
    return doc_list




def get_pdf_splits(pdf_file):
      #Function takes in the pdf data and returns the  splits so for further processing can be done."""
  
  loader = PyPDFLoader(pdf_file)
  pages = loader.load_and_split()  

  textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                             chunk_overlap=15,
                                             length_function=len)
  doc_list = []
  #Pages will be list of pages, so need to modify the loop
  for pg in pages:
    pg_splits = textSplit.split_text(pg.page_content)
    doc_list.extend(pg_splits)

  return doc_list
     



def get_excel_splits(excel_file,target_col,sheet_name):
  trialDF = pd.read_excel(io=excel_file,
                          engine='openpyxl',
                          sheet_name=sheet_name)
  
  df_loader = DataFrameLoader(trialDF,
                              page_content_column=target_col)
  
  excel_docs = df_loader.load()

  return excel_docs


def get_csv_splits(csv_file):
    #  """Function takes in the csv and returns the  splits so for further processing can be done."""
  csvLoader = CSVLoader(csv_file)
  csvdocs = csvLoader.load()
  return csvdocs









def get_git_files(repo_link, folder_path, file_ext):
  # eg. loading only python files
  git_loader = GitLoader(clone_url=repo_link,
    repo_path=folder_path, 
    file_filter=lambda file_path: file_path.endswith(file_ext))
  #Will take each file individual document
  git_docs = git_loader.load()

  textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                             chunk_overlap=15,
                                             length_function=len)
  doc_list = []
  #Pages will be list of pages, so need to modify the loop
  for code in git_docs:
    code_splits = textSplit.split_text(code.page_content)
    doc_list.extend(code_splits)

  return doc_list



def embed_index(doc_list, embed_fn, index_store):
      #Function takes in existing vector_store, new doc_list and embedding function that is 
#   initialized on appropriate model. Local or online. 
#   New embedding is merged with the existing index. If no 
#   index given a new one is created"""
  #check whether the doc_list is documents, or text
  try:
    faiss_db = FAISS.from_documents(doc_list, 
                              embed_fn)  
  except Exception as e:
    faiss_db = FAISS.from_texts(doc_list, 
                              embed_fn)
  
  if os.path.exists(index_store):
    local_db = FAISS.load_local(index_store,embed_fn)
    #merging the new embedding with the existing index store
    local_db.merge_from(faiss_db)
    print("Merge completed")
    local_db.save_local(index_store)
    print("Updated index saved")
  else:
    faiss_db.save_local(folder_path=index_store)
    print("New store created...")



    
def get_docs_length(index_path, embed_fn):
  test_index = FAISS.load_local(index_path,
                              embeddings=embed_fn)
  test_dict = test_index.docstore._dict
  return len(test_dict.values())  


def get_text_splits(text_file):
      #Function takes in the text data and returns the splits so for further processing can be done."""
    with open(text_file,'r') as txt:
        data = txt.read()

    textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                                chunk_overlap=15,
                                                length_function=len)
    doc_list = textSplit.split_text(data)
    return doc_list




def get_pdf_splits(pdf_file):
      #Function takes in the pdf data and returns the  splits so for further processing can be done."""
  
  loader = PyPDFLoader(pdf_file)
  pages = loader.load_and_split()  

  textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                             chunk_overlap=15,
                                             length_function=len)
  doc_list = []
  #Pages will be list of pages, so need to modify the loop
  for pg in pages:
    pg_splits = textSplit.split_text(pg.page_content)
    doc_list.extend(pg_splits)

  return doc_list
     



def get_excel_splits(excel_file,target_col,sheet_name):
  trialDF = pd.read_excel(io=excel_file,
                          engine='openpyxl',
                          sheet_name=sheet_name)
  
  df_loader = DataFrameLoader(trialDF,
                              page_content_column=target_col)
  
  excel_docs = df_loader.load()

  return excel_docs


def get_csv_splits(csv_file):
    #  """Function takes in the csv and returns the  splits so for further processing can be done."""
  csvLoader = CSVLoader(csv_file)
  csvdocs = csvLoader.load()
  return csvdocs




# def get_ipynb_splits(notebook):
#   #Function takes the notebook file,reads the file data as python script, then splits script data directly"""

#   with open(notebook) as fh:
#     nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)

#   exporter = PythonExporter()
#   source, meta = exporter.from_notebook_node(nb)

#   #Python file data is in the source variable
  
#   textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
#                                              chunk_overlap=15,
#                                              length_function=len)
#   doc_list = textSplit.split_text(source)
#   return doc_list  




def get_git_files(repo_link, folder_path, file_ext):
  # eg. loading only python files
  git_loader = GitLoader(clone_url=repo_link,
    repo_path=folder_path, 
    file_filter=lambda file_path: file_path.endswith(file_ext))
  #Will take each file individual document
  git_docs = git_loader.load()

  textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                             chunk_overlap=15,
                                             length_function=len)
  doc_list = []
  #Pages will be list of pages, so need to modify the loop
  for code in git_docs:
    code_splits = textSplit.split_text(code.page_content)
    doc_list.extend(code_splits)

  return doc_list



def embed_index(doc_list, embed_fn, index_store):
      #Function takes in existing vector_store, new doc_list and embedding function that is 
#   initialized on appropriate model. Local or online. 
#   New embedding is merged with the existing index. If no 
#   index given a new one is created"""
  #check whether the doc_list is documents, or text
  try:
    faiss_db = FAISS.from_documents(doc_list, 
                              embed_fn)  
  except Exception as e:
    faiss_db = FAISS.from_texts(doc_list, 
                              embed_fn)
  
  if os.path.exists(index_store):
    local_db = FAISS.load_local(index_store,embed_fn)
    #merging the new embedding with the existing index store
    local_db.merge_from(faiss_db)
    print("Merge completed")
    local_db.save_local(index_store)
    print("Updated index saved")
  else:
    faiss_db.save_local(folder_path=index_store)
    print("New store created...")



    
def get_docs_length(index_path, embed_fn):
  test_index = FAISS.load_local(index_path,
                              embeddings=embed_fn)
  test_dict = test_index.docstore._dict
  return len(test_dict.values())  


# mail_docs = get_text_splits("/content/mail_collector.txt")


def docTrain(training_document, filename, file_format,project_title,user_id):
    print(training_document, filename, file_format,project_title,user_id)
    s3_object = s3_client.get_object(
            Bucket=bucket_name, Key=training_document)
    if file_name_format=="txt":
      mail_docs = get_text_splits("training")
    elif file_name_format=="docx": 
      pass
    elif file_name_format=="pdf": 
      pass
    elif file_name_format=="git": 
      pass
    elif file_name_format=="ipynb": 
      pass
    elif file_name_format=="txt": 
      pass

    pass


def get_UserId(email_id):
    # get the user details for the old email
    # retrieve the user record from the database
    response = table.query(
        KeyConditionExpression='email_id = :email_id',
        ExpressionAttributeValues={
            ':email_id': email_id
        }
    )
    if 'Items' not in response:
        # return an error message if the old email doesn't exist
        return {
            'statusCode': 400,
            'body': json.dumps('Email does not exist')
        }
    user_id = response['Items'][0]['user_id']
    return user_id



def lambda_handler(event, context):
    print(event)
    # TODO implement
    print("Start From Here")

    _start = time.time()
    # print(event)

    #######################################
    #           AWS Information           #
    #######################################
    bucket_name = "crito-ai-primary"


    headers = {k.lower(): v for k, v in event['headers'].items()}
    body = event['body']
    file = _extract_file(headers, body)
    print(file)

    record =event['Records']['body']
      # print(type(record))

    message_body = record['body']
    receipt_handle = record["receiptHandle"]
    print(f"Receipt :  {receipt_handle}")
    message = json.loads(message_body)
    #######################################
    #           Data From Scai            #
    #######################################
    # data = message["data"]
    email_id = message["email_id"]
    project_title = message["project_title"]

    
    use_case= message["use_case"]
    user_id=get_UserId(email_id)
    #######################################
    #      Variable Initialization        #
    #######################################
    final_destination="Tools/Talk To Docs/"
    # paths= `${final_destination}${user_id}/${project_name}/Training Document/${filename}.${file_format}`;
    if use_case=="docTrain":
      training_document= message["training_document"]
      user_id=training_document.split("/")[2]
      filename= message["filename"]
      file_format= message["file_format"]
      if file_format=="xlsx":
            sheet_name=message["sheet_name"]
      status=docTrain(training_document, filename, file_format,project_title,user_id)
      # csv_file_name = f"Content/{user_id}/{project_title}_{req_date}/{content_type}/{file_name}.json"
      check_file = f"{final_destination}/{user_id}/{project_title}/file_name"
      vectorFolder=f"{final_destination}/{user_id}/{project_title}/"
    elif use_case=="checkProject":
      project_title= message["file_name"]
    elif use_case=="chatDoc":
      pass
    # s3_object = s3_client.get_object(Bucket=bucket_name, Key=csv_file_name)
    # data = s3_object['Body'].read()
    # print(data)
    # print(type(data))
    # contents = data.decode('utf-8')
    # json_1 = json.loads(contents)

    # # req_time = req_time.split(":")
    # # json_file = req_time[0]+"-"+req_time[1]
    # #######################################
    # #               Process               #
    # #######################################



    # df_finale = df_final.T.to_dict()
    # for i in df_finale:
    #     #         print(final_df_s3[i])
    #     final_json.append(df_finale[i])

    # if isfile_s3(bucket, output_file) == False:

    #     print(f"--------------Creating File : {output_file}--------------")
    #     response = s3_client.put_object(
    #         Bucket=bucket_name, Key=output_file, Body=json.dumps(final_json))
    #     print(response)

    # else:
    #     print(f"--------------Updating File: {output_file}--------------")

    #     s3_object = s3_client.get_object(
    #         Bucket=bucket_name, Key=output_file)

    #     content = json.loads(s3_object['Body'].read().decode("utf-8"))
    #     content.extend(final_json)
    #     print(f"Updated File Length : {len(content)}")
    #     updated_json = json.dumps(content)
    #     response = s3_client.put_object(
    #         Bucket=bucket_name, Key=output_file, Body=updated_json)
    #     print(response)


    # print("Final Storage")
    # print(df_final.columns)
    # df_fin = df_final.drop(columns=['Class', 'Priority ID',
    #                         'interlinking_article', 'Primary_interlink', 'Primary State', 'Class'])
    # print(df_fin.columns)
    # df_fin = df_fin.T.to_dict()
    # for i in df_fin:
    #     #         print(final_df_s3[i])
    #     fin_json.append(df_fin[i])

    # if isfile_s3(bucket, final_output) == False:

    #     print(
    #         f"--------------Creating File : {final_output}--------------")
    #     response = s3_client.put_object(
    #         Bucket=bucket_name, Key=final_output, Body=json.dumps(fin_json))
    #     print(response)

    # else:
    #     print(
    #         f"--------------Updating File: {final_output}--------------")

    #     s3_object = s3_client.get_object(
    #         Bucket=bucket_name, Key=final_output)

    #     content = json.loads(s3_object['Body'].read().decode("utf-8"))
    #     content.extend(fin_json)
    #     print(f"Updated File Length : {len(content)}")
    #     updated_json = json.dumps(content)
    #     response = s3_client.put_object(
    #         Bucket=bucket_name, Key=final_output, Body=updated_json)
    #     print(response)

    # if content_language != "English":
    #     join["full_file_name"] = final_output
    #     print(f"Sending To Translate in {content_language}")
    #     response_trans = queue_translate_send.send_message(
    #         MessageBody=json.dumps(join))
    #     print(f"Translate Response: {response_trans}")

    # objs = boto3.client('s3').list_objects_v2(
    #     Bucket=bucket_name, Prefix=check_file)
    # fileCount = objs['KeyCount']
    # if fileCount == int(no_keywords) and content_language == "English":
    #     print("All articles has been generated")
    #     response = queue.send_message(MessageBody=json.dumps(join))

    # else:
    #     rem = int(no_keywords-fileCount)
    #     print(f"no of files generated are {fileCount} remaining are {rem}")
    #     print("All Articles Are not generated")


    # print(f"Received and deleted message:  { message_body }")
