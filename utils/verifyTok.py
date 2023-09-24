from fastapi import HTTPException,status
import jwt
import json


def verify_token(token: str,email):
    try:
        secret_key='a4ab7b46652c15cf567a94dd1472562361ef2f85faeabc26401e2f561639f444'
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        if payload['email'] == email:
            return True
        return False
    
    except:
        print("except")
        return False
