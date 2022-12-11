from fastapi import FastAPI, Body, HTTPException
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from User import User
import time
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

import nest_asyncio
nest_asyncio.apply()

load_dotenv("alice.env")

USER_PRIVATE_KEY_FILE = os.getenv('USER_PRIVATE_KEY_FILE')
KADEMLIA_PORT = os.getenv('KADEMLIA_PORT')
RECEIVER_PORT = os.getenv('RECEIVER_PORT')
USER_FILE = os.getenv('USER_FILE')

with open(USER_PRIVATE_KEY_FILE, "rb") as f:
    user_private_key = load_pem_private_key(f.read(), password=None)


import logging
log = logging.getLogger('kademlia')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

# Create the User
user = User(user_private_key, "127.0.0.1", int(KADEMLIA_PORT),int(RECEIVER_PORT), [("127.0.0.1", 6000)], USER_FILE)

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

aliases = {"MCowBQYDK2VwAyEAwM3fp+hoAaYhnxcd4KaP0ngUAVSqbYiHWFz0ralaAVs=": "Zé"}


@app.get("/")   
async def root():
    return {"message": "Hello World"}


@app.get("/timeline")
async def get_timeline():
    posts = user.get_posts()
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

        if (post["author"][27:88] in aliases.keys()):
            post["author_alias"] = aliases[post["author"][27:88]]
        else:
            post["author_alias"] = ""

        transformed_posts.append(transformed_post)
    return transformed_posts


@app.get("/pubkey")
async def get_public_key():
    pubkey = user.public_key[27:87]
    return {"pubkey": pubkey}


@app.get("/subscriptions")
async def get_subscriptions():
    subscribers = user.subscriptions
    res = []
    for subscriber in subscribers:
        pub_key = subscriber[27:87]
        sub = {"pubkey": pub_key, "alias": ""}
        if pub_key in aliases.keys():
            sub["alias"] = aliases[pub_key]
        res.append(sub)

    return res


@app.get("/subscribed")
async def get_subscribed():
    subscribers = user.subscribers
    res = []
    for subscriber in subscribers:
        pub_key = subscriber[27:87]
        res.append({"pubkey": pub_key})

    return res


@app.get("/subscribe")
async def add_subscription(pubkey: str = "", alias: str = ""):
    if (pubkey == ""):
        raise HTTPException(status_code=400, detail="Missing public key")
    pubkey_ = "-----BEGIN PUBLIC KEY-----\n" + \
        pubkey + "\n-----END PUBLIC KEY-----\n"
    print(pubkey_)
    res_code, res_string = user.loop.run_until_complete(user.subscribe(pubkey_))
    if res_code != -2 and alias != "":
        aliases[pubkey] = alias
    return {"detail": res_string}


@app.get("/unsubscribe")
async def remove_subscription(pubkey: str = ""):
    if (pubkey == ""):
        raise HTTPException(status_code=400, detail="Missing public key")
    pubkey_ = "-----BEGIN PUBLIC KEY-----\n" + \
        pubkey + "\n-----END PUBLIC KEY-----\n"
    res_code, res_string = user.loop.run_until_complete(user.unsubscribe(pubkey_))
    return {"detail": res_string}


@app.post("/post")
async def add_post(text: str = Body()):
    if (text == ""):
        raise HTTPException(status_code=400, detail="Missing post text")
    user.loop.run_until_complete(user.create_post(text))
    return {"detail": "Posted successfully!"}
