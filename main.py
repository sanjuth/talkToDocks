from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
from typing import List

from utils.faiss import embed_index, infer, remove_index
from utils.file_split import file_split
from utils.s3 import delete_file_from_s3, upload_file_to_s3
from utils.dynamoDB import check_project_limits, delete_user_chats, fetch_user_chats, fetch_user_projects, get_UserId, store_user_chats, update_user_projects, remove_user_project

from utils.verifyTok import verify_token

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
async def func(
    email: str = Form(...),
    Authentication: str = Header(...),
    projectId: str = Form(...),
    projDate: str = Form(...),
    file: UploadFile = File(...),
):
    print(email)
    print(projectId)
    print(file.filename)
    if not verify_token(Authentication, email):
        return {
            "message": "Authentication failed"
        }
    file_data = await file.read()
    userid = get_UserId(email)
    if userid == 'Email does not exist':
        return {
            'message': userid
        }
    if email != 'hello@gmail.com':
        res = check_project_limits(userid, projectId)
        print(res)
        if not res[0]:
            return {
                "message": res[1]
            }

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_data)
        temp_file_path = temp_file.name

    # uploading doc to S3
    upload_file_to_s3(file.filename, temp_file_path, userid, projectId)

    split_file = file_split(temp_file_path, file.filename)
    embed_index(split_file, projectId, userid)
    print("Doctrain complete")

    # Updating in the user projects table
    print(update_user_projects(userid, projectId, projDate))

    return {
        "message": "Doctrain success"
    }

@app.post("/docChat")
async def func(
    email: str = Form(...),
    Authentication: str = Header(...),
    projectId: str = Form(...),
    query: str = Form(...),
    chatHistory: List[str] = Form(...),
):
    print(email)
    print(projectId)
    print(query)
    print(chatHistory)
    if not verify_token(Authentication, email):
        return {
            "message": "Authentication failed"
        }
    userid = get_UserId(email)
    if userid == 'Email does not exist':
        return {
            'message': userid
        }

    res = infer(projectId, userid, query, chatHistory)
    store_user_chats(userid, projectId, query, res)

    return {
        "result": res
    }

@app.post("/fetchUserProjects")
async def func(
    email: str = Form(...),
    Authentication: str = Header(...),
):
    if not verify_token(Authentication, email):
        raise HTTPException(status_code=401, detail="Authentication failed")
    userid = get_UserId(email)
    if userid == 'Email does not exist':
        return {
            'message': userid
        }
    return fetch_user_projects(userid)

@app.post("/fetchChatHistory")
async def func(
    email: str = Form(...),
    Authentication: str = Header(...),
    projectId: str = Form(...),
):
    if not verify_token(Authentication, email):
        return {
            "message": "Authentication failed"
        }
    userid = get_UserId(email)
    if userid == 'Email does not exist':
        return {
            'message': userid
        }
    return fetch_user_chats(userid, projectId)

@app.post("/deleteUserProj")
async def func(
    email: str = Form(...),
    Authentication: str = Header(...),
    projectId: str = Form(...),
):
    if not verify_token(Authentication, email):
        return {
            "message": "Authentication failed"
        }
    userid = get_UserId(email)
    if userid == 'Email does not exist':
        return {
            'message': userid
        }
    # deleting chat history in DynamoDB
    delete_user_chats(userid, projectId)
    # deleting user project
    remove_user_project(userid, projectId)
    # deleting pdf in S3 bucket
    delete_file_from_s3(userid, projectId)
    # deleting in local index store
    remove_index(projectId, userid)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
