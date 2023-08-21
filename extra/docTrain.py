
# import nbformat
# from nbconvert import PythonExporter
from langchain.embeddings.openai import OpenAIEmbeddings


from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import FAISS
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import (
    PyPDFLoader,
    DataFrameLoader
    # GitLoader
  )
import pandas as pd
import os



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




# def get_git_files(repo_link, folder_path, file_ext):
#   # eg. loading only python files
#   git_loader = GitLoader(clone_url=repo_link,
#     repo_path=folder_path, 
#     file_filter=lambda file_path: file_path.endswith(file_ext))
#   #Will take each file individual document
#   git_docs = git_loader.load()

#   textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
#                                              chunk_overlap=15,
#                                              length_function=len)
#   doc_list = []
#   #Pages will be list of pages, so need to modify the loop
#   for code in git_docs:
#     code_splits = textSplit.split_text(code.page_content)
#     doc_list.extend(code_splits)

#   return doc_list



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
