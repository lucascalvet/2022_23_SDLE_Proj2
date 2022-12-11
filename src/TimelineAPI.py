from fastapi import FastAPI, Body, HTTPException
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from User import User
import time
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

USER_PRIVATE_KEY_FILE = os.getenv('USER_PRIVATE_KEY_FILE')
KADEMLIA_PORT = os.getenv('KADEMLIA_PORT')
RECEIVER_PORT = os.getenv('RECEIVER_PORT')

# Create the User
#user = User(user_private_key, "127.0.0.1", 5678)

app = FastAPI()

origins = [
    "http://localhost:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

posts = [
    {
        "id": 0,
        "text": "Hello, the weather if very nice today!",
        "timestamp": 1670706509,
        "author_alias": "alice",
        "author": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=",
    },
    {
        "id": 1,
        "text": "Hello, the weather if very nice today!",
        "timestamp": 1670706509,
        "author_alias": "bob",
        "author": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=",
    },
    {
        "id": 2,
        "text": "Hello, the weather if very nice today!",
        "timestamp": 1670706509,
        "author_alias": "charlie",
        "author": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=",
    },
    {
        "id": 3,
        "text": "Hello, the weather if very nice today!",
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
    # Transform the timestamp in each post to a date format
    transformed_posts = []
    for post in posts:
        # Convert the timestamp to a date
        date = datetime.fromtimestamp(post["timestamp"])
        # Format the date in the desired format
        formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")

        # Create a new post with the formatted date
        transformed_post = post
        post["formatted_date"] = formatted_date
        transformed_posts.append(transformed_post)
    return transformed_posts


@app.get("/pubkey")
async def get_public_key():
    return {"pubkey": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU="}


@app.get("/subscriptions")
async def get_subscriptions():
    return [
        {"alias": "Zé", "pubkey": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=ze"},
        {"alias": "Fred", "pubkey": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=fred"},
        {"alias": "Rita", "pubkey": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=rita"}
    ]


@app.get("/subscribed")
async def get_subscribed():
    return [
        {"pubkey": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU=ze"},
        {"pubkey": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU="},
        {"pubkey": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU="},
        {"pubkey": "MCowBQYDK2VwAyEAaGHMrIKC3h27SO99YbKEUfUEXDOXjJHYOA5uWHR/rCU="}
    ]


@app.get("/subscribe")
async def add_subscription(pubkey: str = "", alias: str = ""):
    if (pubkey == ""):
        raise HTTPException(status_code=400, detail="Missing public key")
    # TODO: Subscribe here
    return {"pubkey": pubkey}


@app.get("/unsubscribe")
async def add_subscription(pubkey: str = ""):
    if (pubkey == ""):
        raise HTTPException(status_code=400, detail="Missing public key")
    # TODO: Unsubscribe here
    return {"pubkey": pubkey}


@app.post("/post")
async def add_post(text: str = Body()):
    # TODO: Create post here

    timestamp = time.time()
    posts.append(
        {
            "id": -1,
            "text": text,
            "timestamp": timestamp,
            "author_alias": "myself",
            "author": "whatever",
        }
    )
    return {"message": "Posted successfully!"}
