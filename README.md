# Zchat

[![License: MIT](https://shields.io)](https://opensource.org)
[![Python 3.10+](https://shields.io)](https://python.org)
[![FastAPI](https://shields.io)](https://tiangolo.com)

A simple, lightweight WebSocket chat server built with **FastAPI** and **Python `asyncio`**. This project serves as a clean, working foundation with UUID-based sessions, message routing, background connection cleanup, and a CLI client—designed to be expanded with more features over time.

---

## Features

* **Real-Time Bidirectional Messaging:** Built on FastAPI WebSockets for low-latency text communication.
* **Automatic UUID Session Tracking:** Assigns every connected client a unique `uuid4` identifier stored in an in-memory `O(1)` hashmap (`ConnectionHandler`).
* **Flexible Message Routing:**
  * **Public Broadcast:** Send messages to all connected clients.
  * **Direct Messaging (`<<`):** Send private 1-on-1 messages to a specific client UUID.
  * **Targeted Group Broadcast (`<<<`):** Send messages to a comma-separated list of client UUIDs.
* **Background Stale-Connection Cleanup:** Uses FastAPI's `lifespan` manager and an `asyncio` background task to periodically ping and purge disconnected sockets.
* **Interactive CLI Client:** Includes a non-blocking `asyncio` + `argparse` terminal client (`client.py`) for connecting locally or over a network.

---

## Project Structure

```text
zchat/
├── main.py                        # FastAPI app, lifespan cleanup, and /ws endpoint
├── client.py                      # Interactive CLI WebSocket client with argparse
├── classes/
│   └── connection_handler.py      # Connection lifecycle, routing, and cleanup logic
├── models/
│   └── connection_model.py        # Pydantic model storing socket metadata & UUID
├── handlers/
│   └── cleanup_handler.py         # Periodic background task for dead sockets
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting Started

### 1. Prerequisites
* Python 3.10+
* `pip` and a virtual environment (`venv`)

### 2. Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com
cd zchat
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install "fastapi[standard]" uvicorn pydantic websockets
```

### 3. Start the Server
Run the FastAPI server in development mode:

```bash
fastapi dev main.py
```

Or using Uvicorn directly (keep `--workers 1` so all clients share the in-memory connection pool):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

Verify the server is running by visiting `http://127.0.0` (returns `"running"`).

---

## Using the CLI Client

Open two or more terminal windows (with your virtual environment activated) and run:

```bash
python client.py
```

Upon connecting, the server assigns and displays your unique connection ID:

```text
[SERVER]
Connected to the server
id:[78d8c91a-d157-4ae6-a6c2-ea3db006ac42]
==================================================
```

### CLI Options (`argparse`)

| Flag | Description | Default |
| :--- | :--- | :--- |
| `-u`, `--uri` | Full WebSocket URI (overrides `--host` and `--port`) | `None` |
| `-H`, `--host` | Server hostname or IP address | `127.0.0.1` |
| `-p`, `--port` | Server port | `8000` |
| `--ssl` | Use `wss://` instead of `ws://` | `False` |

**Examples:**
```bash
# Connect to a custom host and port on your local network
python client.py --host 192.168.1.15 --port 8000

# Connect to a deployed secure WebSocket server
python client.py --uri wss://://onrender.com
```

---

## Message Protocol

| Action | Syntax | Example |
| :--- | :--- | :--- |
| **Public Broadcast** | `<message>` | `Hello everyone!` |
| **Private Direct Message** | `<target_uuid><< <message>` | `2712670c-f2b7-43d3-9340-2add037da941<<Hey!` |
| **Targeted Group Broadcast** | `<uuid1>,<uuid2><<< <message>` | `uuid1,uuid2<<<Secret group update` |
| **Client Commands** | `/help`, `/quit`, `/exit` | `/quit` |

---

## Roadmap & Future Improvements

* [ ] Custom usernames and display names
* [ ] Named chat rooms / channels
* [ ] Structured JSON message payloads
* [ ] Optional Redis Pub/Sub support for multi-worker scaling

---

## License

This project is licensed under the [MIT License](LICENSE.md).
