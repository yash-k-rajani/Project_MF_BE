from fastapi.middleware.cors import CORSMiddleware
from main import app


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)
