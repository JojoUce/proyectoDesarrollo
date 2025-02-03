#pip install fastapi uvicorn
#uvicorn Folder.main:app --reload
#uvicorn Folder.main:app --reload --host 0.0.0.0 --port 8080
#ngrok config add-authtoken 2qEYbjvpypjY1pCfnvRxsMPsR05_4zdeyB2yYqhLHGtmX7pTc
#ngrok  http 8080

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}





