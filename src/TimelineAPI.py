from fastapi import FastAPI, Body
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from .User import User
import time 
from fastapi.middleware.cors import CORSMiddleware
# Create the User
# user = User(user_private_key, "127.0.0.1", 5678)

app = FastAPI()

origins = [
    "http://localhost:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Fix this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

posts = [
    {
        "id": 0,
        "text": "Hello, the wheather if very nice today!",
        "timestamp": 1670706509,
        "author_alias": "alice",
        "author": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=",
    },
    {
        "id": 1,
        "text": "Hello, the wheather if very nice today!",
        "timestamp": 1670706509,
        "author_alias": "bob",
        "author": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=",
    },
    {
        "id": 2,
        "text": "Hello, the wheather if very nice today!",
        "timestamp": 1670706509,
        "author_alias": "charlie",
        "author": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=",
    },
    {
        "id": 3,
        "text": "Hello, the wheather if very nice today!",
        "timestamp": 1670706509,
        "author_alias": "david",
        "author": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=",
    }
]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/timeline")
async def get_timeline():
    return posts


@app.post("/post")
async def add_post(text: str = Body()):
    # TODO: Create post here
    posts.append(
        {
            "id": -1,
            "text": text,
            "timestamp": time.time(),
            "author_alias": "myself",
            "author": "whatever",
        }
    )
    return {"message": "Posted successfully!"}
