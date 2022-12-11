## Running Instructions

### Configure the current user

Change the `.env` file to configure the user before running its local API (or write the path to the environment file in `load_dotenv` of `TimelineAPI.py`).
The API will set up the user and expose endpoints for interacting with it.

```
USER_PRIVATE_KEY_FILE=keys/bob
KADEMLIA_PORT=5678
RECEIVER_PORT=5000
```

### Run the API

Making sure to have installed the requirements, run the following command do serve the API.

```
uvicorn TimelineAPI:app --port <api port>
```

### Run the bootstrapper

Use `bootstrap.env` in `load_dotenv` of `TimelineAPI.py`:

```sh
uvicorn TimelineAPI:app --port <api port>
```

### Run the frontend

The frontend allows for an easy interaction with the API, and, in turn, with the local user.
To run the frontend, run the following commands on the `frontend` directory.

```
npm run build
npm install -g serve
serve -s build
```

To access the frontend, navigate to:

```
http://localhost:3000/?api=http://localhost:<api port>/
```

Where the `api port` is the port for the API you want to interact with
