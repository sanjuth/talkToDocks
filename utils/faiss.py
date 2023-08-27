from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI

import os
import shutil
from dotenv.main import load_dotenv

load_dotenv()

OpenAI_KEY = os.environ["OPENAI_API_KEY"]

embeddings = OpenAIEmbeddings(
    openai_api_key=OpenAI_KEY)


# index_store is projectID

def embed_index(doc_list, index_store, userid):
    """Function takes in existing vector_store,
    new doc_list and embedding function that is
    initialized on appropriate model. Local or online.
    New embedding is merged with the existing index. If no
    index given a new one is created"""
    # check whether the doc_list is documents, or text
    try:
        faiss_db = FAISS.from_documents(doc_list, embeddings)
    except Exception as e:
        faiss_db = FAISS.from_texts(doc_list, embeddings)

    if os.path.exists(os.path.join("FAISS_INDEX_STORE", userid, index_store)):
        local_db = FAISS.load_local(os.path.join(
            "FAISS_INDEX_STORE", userid, index_store), embeddings)
        # merging the new embedding with the existing index store
        local_db.merge_from(faiss_db)
        print("Merge completed")
        local_db.save_local(index_store)
        print("Updated index saved")
    else:
        faiss_db.save_local(folder_path=os.path.join(
            "FAISS_INDEX_STORE", userid, index_store))
        print("New store created...")


def remove_index(index_store, userid):
    try:
        shutil.rmtree(os.path.join("FAISS_INDEX_STORE", userid, index_store))
        print("index removed form local store successfully...")
    except:
        print("Failed to delete from local index")


def convert_to_tuples(chat_list):
    chat_tuples = []
    if not chat_list or len(chat_list) <= 1:
        return chat_tuples
    for i in range(0, len(chat_list), 2):
        query = chat_list[i]
        response = chat_list[i + 1]
        chat_tuples.append((query, response))
    return chat_tuples


def infer(index_store, userid, query, chatHistory):
    history = convert_to_tuples(chatHistory)
    if not os.path.exists(os.path.join("FAISS_INDEX_STORE", userid, index_store)):
        return "Invalid project Id or email"
    vectorstore = FAISS.load_local(os.path.join(
        "FAISS_INDEX_STORE", userid, index_store), embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 20})
    qa = ConversationalRetrievalChain.from_llm(OpenAI(
        temperature=0, openai_api_key=OpenAI_KEY), retriever)
    result = qa({"question": query, "chat_history": history})
    return result["answer"]
