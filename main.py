from fastapi import FastAPI

app = FastAPI()

from router import middleware
from router import file_process


@app.get("/")
def read_root():
    return {"message": "YASH the Killer!!"}


app.include_router(file_process.router)
