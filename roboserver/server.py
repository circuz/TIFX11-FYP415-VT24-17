import os
import time
import struct
import hashlib
import asyncio
import datetime
import shutil
import json
from pathlib import Path
from aiohttp import web

WS_HASH = b"\x00"
WS_EXPERIMENT_UPLOAD_START = b"\x01"
WS_EXPERIMENT_UPLOAD_CODE = b"\x02"
WS_EXPERIMENT_UPLOAD_END = b"\x03"
WS_EXPERIMENT_UPLOAD_CONTINUE = b"\x04"
WS_RESET = b"\x05"
WS_EXPERIMENT_ERROR = b"\x06"
WS_EXPERIMENT_EXITED = b"\x07"
WS_TELEMETRY = b"\x08"
WS_EXPERIMENT_START = b"\x09"
WS_EXPERIMENT_STOP = b"\x0a"
WS_RENAME = b"\x0b"
WS_EXPERIMENT_MESSAGE = b"\x0c"

STATE_INIT = 1
STATE_RUNNING = 2
STATE_STOPPED = 3
STATE_ERROR = 4
STATE_EXITED = 5

static_path = Path("frontend/dist")
experiment_path = Path("experiment.py")
experiment_data_path = Path("experiments")
current_experiment_data_path = None

routes = web.RouteTableDef()


robo_sockets = set()
user_sockets = set()
experiment_running = False


@routes.get("/")
async def index(request):
    return web.Response(
        body=(static_path / "index.html").read_bytes(), content_type="text/html"
    )


async def create_state_dict():
    return {
        "type": "state",
        "experiment_running": experiment_running,
        "experiment_hash": hashlib.md5(experiment_path.read_text().encode())
        .digest()
        .hex(),
    }


async def send_to_users(msg):
    for user_socket in user_sockets:
        await user_socket.q.put(msg)


class UserSocket:
    def __init__(self, request, ws):
        self.request = request
        self.ws = ws
        self.q = asyncio.Queue()

    async def handle(self):
        self.sender_task = asyncio.create_task(self.sender())
        self.receiver_task = asyncio.create_task(self.receiver())

        try:
            while True:
                if (
                    self.sender_task.done()
                    or self.receiver_task.done()
                    or self.ws.closed
                ):
                    try:
                        e = self.sender_task.exception()
                        if e:
                            print(repr(e))
                            raise e
                    except asyncio.exceptions.InvalidStateError:
                        pass
                    try:
                        e = self.receiver_task.exception()
                        if e:
                            print(repr(e))
                            raise e
                    except asyncio.exceptions.InvalidStateError:
                        pass

                await asyncio.sleep(0.05)
        finally:
            self.sender_task.cancel()
            self.receiver_task.cancel()

    async def sender(self):
        while True:
            msg = await self.q.get()
            await self.ws.send_json(msg)

    async def receiver(self):
        global experiment_running, current_experiment_data_path
        async for msg in self.ws:
            data = msg.json()

            if data["type"] == "upload":
                if data["code"] != experiment_path.read_text():
                    experiment_path.write_text(data["code"])

                    await send_to_robots(WS_EXPERIMENT_UPLOAD_START)
                await self.q.put(await create_state_dict())

            if data["type"] == "run":
                current_experiment_data_path = (
                    experiment_data_path
                    / f'{data["filename"]}-{datetime.datetime.now().isoformat()}'
                )
                current_experiment_data_path.mkdir()
                shutil.copy(
                    experiment_path, current_experiment_data_path / "experiment.py"
                )
                print(f"starting experiment {current_experiment_data_path.name}")

                experiment_running = True
                await self.q.put(await create_state_dict())
                await send_to_robots(WS_EXPERIMENT_START)

            if data["type"] == "stop":
                experiment_running = False
                await self.q.put(await create_state_dict())
                await send_to_robots(WS_EXPERIMENT_STOP)
                print("stopped experiment")


@routes.get("/user_ws")
async def user_ws(request):
    ws = web.WebSocketResponse(heartbeat=10)
    await ws.prepare(request)

    print("user connected")

    await ws.send_json(
        {
            "type": "init",
            "code": experiment_path.read_text(),
        }
    )

    await ws.send_json(await create_state_dict())

    user_socket = UserSocket(request, ws)
    user_sockets.add(user_socket)

    try:
        await user_socket.handle()
    finally:
        user_sockets.remove(user_socket)
        print("user disconnected")


async def send_to_robots(msg):
    for robo_socket in robo_sockets:
        await robo_socket.q.put(msg)


class RoboSocket:
    upload_counter = 0
    uploading = False

    def __init__(self, request, ws):
        self.ws = ws
        self.request = request
        self.q = asyncio.Queue()
        self.experiment_code = experiment_path.read_bytes()

    async def handle(self):
        self.sender_task = asyncio.create_task(self.sender())
        self.receiver_task = asyncio.create_task(self.receiver())

        try:
            while True:
                if (
                    self.sender_task.done()
                    or self.receiver_task.done()
                    or self.ws.closed
                ):
                    try:
                        e = self.sender_task.exception()
                        if e:
                            print(repr(e))
                            raise e
                    except asyncio.exceptions.InvalidStateError:
                        pass
                    try:
                        e = self.receiver_task.exception()
                        if e:
                            print(repr(e))
                            raise e
                    except asyncio.exceptions.InvalidStateError:
                        pass

                await asyncio.sleep(0.05)
        finally:
            self.sender_task.cancel()
            self.receiver_task.cancel()

    async def sender(self):
        while True:
            msg = await self.q.get()
            if msg == WS_EXPERIMENT_UPLOAD_START:
                self.upload_counter = 0
                self.uploading = True
                self.experiment_code = experiment_path.read_bytes()
            await self.ws.send_bytes(msg)

    async def receiver(self):
        async for msg in self.ws:

            if msg.data[0] == ord(WS_EXPERIMENT_UPLOAD_CONTINUE) and self.uploading:
                chunk = self.experiment_code[
                    self.upload_counter * 1024 : (self.upload_counter + 1) * 1024
                ]
                if len(chunk) > 0:
                    print(
                        f"{self.request.match_info['name']} uploading chunk {self.upload_counter}"
                    )
                    await self.q.put(WS_EXPERIMENT_UPLOAD_CODE + chunk)
                else:
                    await self.q.put(WS_EXPERIMENT_UPLOAD_END)
                    self.uploading = False
                    print(f"{self.request.match_info['name']} upload done")
                self.upload_counter += 1

            elif msg.data[0] == ord(WS_TELEMETRY):
                # DIY ping mechanism, because real pings seem to be broken with the micropython lib
                asyncio.create_task(self.q.put(WS_TELEMETRY))

                (experiment_hash, state) = struct.unpack("16sB", msg.data[1:])

                await send_to_users(
                    {
                        "type": "telemetry",
                        "name": self.request.match_info["name"],
                        "experiment_hash": experiment_hash.hex(),
                        "state": state,
                    }
                )

                h = hashlib.md5()
                h.update(self.experiment_code)

                if experiment_hash != h.digest() and not self.uploading:
                    print(
                        f"{self.request.match_info['name']} uploading new code to robot"
                    )
                    await self.q.put(WS_EXPERIMENT_UPLOAD_START)

                if experiment_running and state == STATE_STOPPED:
                    await self.q.put(WS_EXPERIMENT_START)

                if not experiment_running and state == STATE_RUNNING:
                    await self.q.put(WS_EXPERIMENT_STOP)

            elif msg.data[0] == ord(WS_EXPERIMENT_MESSAGE):
                with (
                    current_experiment_data_path / self.request.match_info["name"]
                ).open("a") as f:
                    f.write(
                        json.dumps(
                            {
                                "type": "message",
                                "message": msg.data[1:].decode(),
                                "time": time.time(),
                            }
                        )
                    )
                    f.write("\n")
                print(
                    f"experiment message from robot {self.request.match_info['name']}: {msg.data[1:]}"
                )

            else:
                print(
                    f"Unexpected message from {self.request.match_info['name']}: {msg.data!r}"
                )


@routes.get("/robo_ws/{name}")
async def robo_ws(request):
    ws = web.WebSocketResponse(receive_timeout=15)
    await ws.prepare(request)

    print(f"robot {request.match_info['name']} connected")

    if request.match_info["name"] == "undefined":
        name = os.urandom(8).hex()
        print(f"renaming robot to {name}")
        await ws.send_bytes(WS_RENAME + name.encode() + b"\x00" * 16)
    else:
        robo_socket = RoboSocket(request, ws)
        robo_sockets.add(robo_socket)

        await robo_socket.handle()

        robo_sockets.remove(robo_socket)

    print(f"robot {request.match_info['name']} disconnected")


routes.static("/", static_path)

app = web.Application()
app.add_routes(routes)
web.run_app(app)
