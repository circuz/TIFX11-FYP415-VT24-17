import asyncio
import hashlib
import machine
import sys
from collections import deque
from ws import AsyncWebsocketClient
from hardware import Robot
from selftest import selftest
import io

WS_HASH = b"\x00"
WS_EXPERIMENT_UPLOAD_START = b"\x01"
WS_EXPERIMENT_UPLOAD_CODE = b"\x02"
WS_EXPERIMENT_UPLOAD_END = b"\x03"
WS_EXPERIMENT_UPLOAD_CONTINUE = b"\x04"
WS_RESET = b"\x05"
WS_EXPERIMENT_ERROR = b"\x06"
WS_EXPERIMENT_EXITED = b"\x07"

STATE_INIT = 1
STATE_RUNNING = 2
STATE_STOPPED = 3
STATE_ERROR = 4
STATE_EXITED = 5

state = STATE_INIT

send_queue = deque((), 32)

event_stop_experiment = asyncio.Event()
event_stop_experiment.set()
event_start_experiment = asyncio.Event()
event_start_experiment.set()


async def ws_sender(ws):
    while True:
        if len(send_queue) > 0:
            m = send_queue.popleft()
            await ws.send(m)

        await asyncio.sleep(0.1)


async def ws_receiver(ws):
    while True:
        m = await ws.recv()
        print(m)

        if m[0] == ord(WS_EXPERIMENT_UPLOAD_START):
            event_stop_experiment.clear()
            await event_stop_experiment.wait()
            f = open("experiment.py", "wb")
            send_queue.append(WS_EXPERIMENT_UPLOAD_CONTINUE)
        if m[0] == ord(WS_EXPERIMENT_UPLOAD_CODE):
            f.write(m[1:])
            send_queue.append(WS_EXPERIMENT_UPLOAD_CONTINUE)
        if m[0] == ord(WS_EXPERIMENT_UPLOAD_END):
            f.close()
            event_start_experiment.clear()
        if m[0] == ord(WS_RESET):
            machine.reset()


async def experiment_wrapper():
    # reimport the experiment
    if "experiment" in sys.modules:
        del sys.modules["experiment"]

    from experiment import run

    robot = Robot()
    await robot.init()

    try:
        await run(robot)
    except asyncio.CancelledError:
        # reinit to stop any motors and leds
        await robot.init()  # TODO does this start conflicting threads?
        return None
    except Exception as e:
        return e


async def main():
    global state
    robot = Robot()
    await robot.init()

    experiment_task = asyncio.create_task(experiment_wrapper())
    state = STATE_RUNNING

    # wait until network is available
    sta_if = network.WLAN(network.STA_IF)
    while not sta_if.isconnected():
        await asyncio.sleep(0.1)

    sta_if = network.WLAN(network.STA_IF)

    ws = AsyncWebsocketClient()
    if not await ws.handshake(f"ws://{sta_if.ifconfig()[2]}:8080/robo_ws"):
        print("ws handshake failed")
        return

    if not (await ws.open()):
        print("ws open failed")
        return

    # send hash of current experiment code
    h = hashlib.md5()
    with open("experiment.py", "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            h.update(data)

    await ws.send(WS_HASH + h.digest())

    asyncio.create_task(ws_sender(ws))
    asyncio.create_task(ws_receiver(ws))

    # TODO check ws state

    while True:
        if not event_stop_experiment.is_set():
            experiment_task.cancel()
            event_stop_experiment.set()
            state = STATE_STOPPED

        if not event_start_experiment.is_set():
            experiment_task = asyncio.create_task(experiment_wrapper())
            event_start_experiment.set()
            state = STATE_RUNNING

        if state == STATE_RUNNING and experiment_task.done():
            result = await experiment_task
            if isinstance(result, Exception):
                state = STATE_ERROR
                b = io.BytesIO()
                sys.print_exception(result, b)
                b.seek(0)
                send_queue.append(WS_EXPERIMENT_ERROR + b.read())
                del b
            if result is None:
                state = STATE_EXITED
                send_queue.append(WS_EXPERIMENT_EXITED)

        await asyncio.sleep(0.1)


asyncio.run(main())
