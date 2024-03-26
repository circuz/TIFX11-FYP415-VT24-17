import sys
from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosedError


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

    print("Starting selftest...")
    ws.send("\x03")
    ws.send("\n")
    ws.send("selftest()\r\n")
    resp = ""
    while True:
        r = ws.recv()
        resp += r
        print(r, end="", flush=True)
        if "SELFTEST: PASS" in resp or "SELFTEST: FAIL" in resp:
            break
