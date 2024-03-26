import hashlib
from pathlib import Path
from aiohttp import web, WSMsgType

WS_HASH = b"\x00"
WS_EXPERIMENT_UPLOAD_START = b"\x01"
WS_EXPERIMENT_UPLOAD_CODE = b"\x02"
WS_EXPERIMENT_UPLOAD_END = b"\x03"
WS_EXPERIMENT_UPLOAD_CONTINUE = b"\x04"
WS_RESET = b"\x05"

routes = web.RouteTableDef()


@routes.get("/")
async def index(request):
    return web.Response(body=Path("index.html").read_bytes(), content_type="text/html")


@routes.get("/robo_ws")
async def robo_ws(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("robot connecting")

    upload_counter = 0
    experiment_code = b""

    async for msg in ws:
        if msg.type == WSMsgType.PING:
            await ws.pong(msg.data)
            continue

        print(msg.data)

        if msg.data[0] == ord(WS_HASH):
            print("hash message")
            experiment_code = Path("experiment.py").read_bytes()
            h = hashlib.md5()
            h.update(experiment_code)

            if msg.data[1:] != h.digest():
                print("uploading new code to robot")
                upload_counter = 0
                await ws.send_bytes(WS_EXPERIMENT_UPLOAD_START)

        if msg.data[0] == ord(WS_EXPERIMENT_UPLOAD_CONTINUE):
            chunk = experiment_code[upload_counter * 1024 : (upload_counter + 1) * 1024]
            if len(chunk) > 0:
                print(f"uploading chunk {upload_counter}")
                await ws.send_bytes(WS_EXPERIMENT_UPLOAD_CODE + chunk)
            else:
                await ws.send_bytes(WS_EXPERIMENT_UPLOAD_END)
                print("upload done")
            upload_counter += 1


app = web.Application()
app.add_routes(routes)
web.run_app(app)
