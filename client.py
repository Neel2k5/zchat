import argparse
import asyncio
import sys
import websockets


def parse_args():
    parser = argparse.ArgumentParser(
        description="Zchat CLI Client"
    )
    parser.add_argument(
        "-u", "--uri",
        type=str,
        default=None,
        help="Full WebSocket URI (e.g., wss://zchat.onrender.com/ws). Overrides --host and --port."
    )
    parser.add_argument(
        "-H", "--host",
        type=str,
        default="127.0.0.1",
        help="Server host address (default: 127.0.0.1)"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        help="Use secure WebSocket protocol (wss://) when building from --host and --port"
    )
    return parser.parse_args()


async def receive_messages(ws):
    try:
        async for message in ws:
            if message in ("[PING]", b"SERVER_PING"):
                continue

            print(f"\r{message}\n> ", end="", flush=True)
    except websockets.ConnectionClosed:
        print("\n[Disconnected from server]")


async def send_messages(ws):
    loop = asyncio.get_running_loop()
    while True:
        msg = await loop.run_in_executor(None, input, "> ")
        clean_msg = msg.strip()

        if not clean_msg:
            continue

        if clean_msg.lower() in {"/quit", "/exit"}:
            await ws.close()
            break

        if clean_msg == "/help":
            print(
                "\nCommands:\n"
                "  <message>                -> Broadcast to everyone\n"
                "  <id><<message>           -> Private message to one user\n"
                "  <id1>,<id2><<<message>   -> Group message to selected users\n"
                "  /quit                    -> Exit chat\n"
            )
            continue

        await ws.send(clean_msg)


async def main():
    args = parse_args()

    if args.uri:
        uri = args.uri
    else:
        scheme = "wss" if args.ssl else "ws"
        uri = f"{scheme}://{args.host}:{args.port}/ws"

    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as ws:
            print("Type /help for message formats.\n")
            await asyncio.gather(
                receive_messages(ws),
                send_messages(ws),
            )
    except ConnectionRefusedError:
        print(f"Connection refused at {uri}. Make sure the server is running.")
    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting Zchat...")
        sys.exit(0)
