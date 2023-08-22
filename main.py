from fastapi import FastAPI, File, UploadFile, Form, Request
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
from typing import List
from pydantic import BaseModel


from utils.faiss import embed_index, infer, remove_index
from utils.file_split import file_split
from utils.s3 import delete_file_from_s3, upload_file_to_s3
from utils.dynamoDB import delete_user_chats, get_UserId, store_user_chats



app = FastAPI(
    title="talk to docs API",
    description="",
    version="0.0.1",
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/notify/v1/health')
def get_health():
    return dict(msg='OK')

@app.post("/doctrain")
async def func(email: str=Form(...),projectId: str=Form(...),file: UploadFile = File(...)):
    print(email)
    print(projectId)
    print(file.filename)
    file_data = await file.read()
    userid=get_UserId(email)
    userid=email #TESTING PURPOSE REMOVE THIS LINE
    if userid == 'Email does not exist':
        return{
            'message': userid
        }
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_data)
        temp_file_path = temp_file.name

    #uploading doc to S3
    upload_file_to_s3(file.filename, temp_file_path, userid, projectId )

    split_file = file_split(temp_file_path,file.filename)
    embed_index(split_file, projectId ,userid)
    print("Doctrain complete")
    return {
        "message": "Doctrain success"
    }


class StringListInput(BaseModel):
    items: List[str]


@app.post("/docChat")
async def func(email: str=Form(...),projectId: str=Form(...),query: str=Form(...),chatHistory: List[str]=Form(...)):
    print(email)
    print(projectId)
    print(query)
    print(chatHistory)

    userid=get_UserId(email)
    userid=email #TESTING PURPOSE REMOVE THIS LINE
    if userid == 'Email does not exist':
        return{
            'message': userid
        }
    res = infer(projectId,userid,query,chatHistory)
    store_user_chats(userid,projectId,query,res)
    return{
        "result": res
    }

@app.post("/deleteChat")
async def func(email: str=Form(...), projectId: str=Form(...)):
    userid=get_UserId(email)
    userid=email #TESTING PURPOSE REMOVE THIS LINE
    if userid == 'Email does not exist':
        return{
            'message': userid
        }
    
    try:
        #deleting chat history in dynamoBD
        delete_user_chats(userid,projectId)
        #deleting pdf in S3 bucket
        delete_file_from_s3(userid,projectId)
        #deleting in local index store
        remove_index(projectId,userid)
    except:
        print("something went wrong while removing the chat")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)