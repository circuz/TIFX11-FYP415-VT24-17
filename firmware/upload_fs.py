import sys
import struct
from pathlib import Path
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedError

if len(sys.argv) < 2:
    print("Usage: python upload_fs.py <ip>")
    exit()

# pack the whole fs into a list
files = [
    (
        str(path.relative_to("filesystem")),
        (None if path.is_dir() else path.read_bytes()),
    )
    for path in Path("filesystem").glob("**/*")
]

# create boot.py file that updates the fs
boot = Path("update_boot.py").read_text().replace("$$FILES$$", str(files)).encode()

with connect(f"ws://{sys.argv[1]}:8266") as ws:

    try:
        ws.recv(timeout=3)  # "Password:"
    except ConnectionClosedError:
        print("Could not connect! Is another WebREPL running?")
        exit(1)

    # enter password
    print("Authenticating")
    ws.send("roboting\n")
    if "WebREPL connected" not in ws.recv(timeout=3):
        print("Could not authenticate!")
        exit(1)

    print("Stopping current program")
    ws.send("\x03")
    ws.send("UPLOAD_MARKER\n")
    resp = ""
    while True:
        resp += ws.recv()
        if "UPLOAD_MARKER" in resp:
            break

    # send file upload request, see https://github.com/micropython/webrepl/blob/master/webrepl_cli.py
    print("Sending file upload request")
    ws_req = struct.pack(
        "<2sBBQLH64s", b"WA", 1, 0, 0, len(boot), len("boot.py"), b"boot.py"
    )
    ws.send(ws_req)
    while not isinstance(resp := ws.recv(), bytes):
        pass
    if resp != b"WB\x00\x00":
        print("File upload request failed!", resp)
        exit(1)

    # send file in 1024 bytes chunks
    print("Sending boot.py")
    for chunk in [boot[i : i + 1024] for i in range(0, len(boot) - 1, 1024)]:
        ws.send(chunk)
    while not isinstance(resp := ws.recv(), bytes):
        pass
    if resp != b"WB\x00\x00":
        print("File upload failed!", resp)
        exit(1)

    # reset MCU if repl is available
    print("Attempting to reset MCU")
    ws.send("\x03")  # ctrl-c
    ws.send("import machine; machine.reset()\r\n")

    print("Done!")

    import time

    time.sleep(1)

    ws.close_socket()
