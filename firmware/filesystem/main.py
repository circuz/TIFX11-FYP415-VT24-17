import sys
import os
import io
import time
import struct
import asyncio
import hashlib
import machine
import neopixel
from micropython import const
from collections import deque
from ws import AsyncWebsocketClient
from hardware import Robot, PIN_LED_STATUS

WS_HASH = const(b"\x00")
WS_EXPERIMENT_UPLOAD_START = const(b"\x01")
WS_EXPERIMENT_UPLOAD_CODE = const(b"\x02")
WS_EXPERIMENT_UPLOAD_END = const(b"\x03")
WS_EXPERIMENT_UPLOAD_CONTINUE = const(b"\x04")
WS_RESET = const(b"\x05")
WS_EXPERIMENT_ERROR = const(b"\x06")
WS_EXPERIMENT_EXITED = const(b"\x07")
WS_TELEMETRY = const(b"\x08")
WS_EXPERIMENT_START = const(b"\x09")
WS_EXPERIMENT_STOP = const(b"\x0a")
WS_RENAME = const(b"\x0b")

STATE_INIT = const(1)
STATE_RUNNING = const(2)
STATE_STOPPED = const(3)
STATE_ERROR = const(4)
STATE_EXITED = const(5)

state = STATE_INIT

state_colors = {
    STATE_INIT: const((1, 0, 1)),
    STATE_RUNNING: const((0, 1, 0)),
    STATE_STOPPED: const((1, 1, 0)),
    STATE_ERROR: const((1, 0, 0)),
    STATE_EXITED: const((6, 1, 0)),
}

NET_STATE_DISCONNECTED = const(1)
NET_STATE_WIFI_CONNECTED = const(2)
NET_STATE_WS_CONNECTED = const(3)

net_state = NET_STATE_DISCONNECTED

net_state_timings = {
    NET_STATE_DISCONNECTED: const((0.9, 0.1)),
    NET_STATE_WIFI_CONNECTED: const((0.5, 0.5)),
    NET_STATE_WS_CONNECTED: const((0.1, 0.9)),
}

send_queue = deque((), 32)

event_stop_experiment = asyncio.Event()
event_stop_experiment.set()
event_start_experiment = asyncio.Event()
event_start_experiment.set()

persistent_state_file_path = "state"
persistent_state = {"running": False, "name": b"undefined"}

experiment_hash = ""


def update_experiment_hash():
    global experiment_hash
    h = hashlib.md5()
    with open("experiment.py", "rb") as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            h.update(data)

    experiment_hash = h.digest()


update_experiment_hash()


def save_persistent_state():
    with open(persistent_state_file_path, "wb") as f:
        f.write(struct.pack("B32s", state == STATE_RUNNING, persistent_state["name"]))


def load_persistent_state():
    global persistent_state
    with open(persistent_state_file_path, "rb") as f:
        running, name = struct.unpack("B32s", f.read())
        persistent_state = {"running": running == 1, "name": name.rstrip(b"\x00")}


# add timeout detection
class TimingAsyncWebsocketClient(AsyncWebsocketClient):
    last_frame = 0

    async def read_frame(self, *args, **kwargs):
        frame = await super().read_frame(*args, **kwargs)
        self.last_frame = time.time()
        return frame

    async def handshake(self, *args, **kwargs):
        status = await super().handshake(*args, **kwargs)
        self.last_frame = time.time()
        return status


async def ws_handler():
    global net_state
    # wait until network is available
    sta_if = network.WLAN(network.STA_IF)
    while not sta_if.isconnected():
        net_state = NET_STATE_DISCONNECTED
        await asyncio.sleep(0.1)

    net_state = NET_STATE_WIFI_CONNECTED

    ws = TimingAsyncWebsocketClient()
    try:
        if not await ws.handshake(
            f"ws://{sta_if.ifconfig()[2]}:8080/robo_ws/{persistent_state['name'].decode()}"
        ):
            print("ws handshake failed")
            return
    except OSError:
        await asyncio.sleep(5)
        return

    if not (await ws.open()):
        print("ws open failed")
        return

    net_state = NET_STATE_WS_CONNECTED

    # send hash of current experiment code
    # h = hashlib.md5()
    # with open("experiment.py", "rb") as f:
    #     while True:
    #         data = f.read(1024)
    #         if not data:
    #             break
    #         h.update(data)

    # await ws.send(WS_HASH + h.digest())

    sender_task = asyncio.create_task(ws_sender(ws))
    receiver_task = asyncio.create_task(ws_receiver(ws))

    while True:
        if (
            ws.last_frame + 10 < time.time()
            or sender_task.done()
            or receiver_task.done()
        ):
            if sta_if.isconnected():
                net_state = NET_STATE_WIFI_CONNECTED
            else:
                net_state = NET_STATE_DISCONNECTED
            sender_task.cancel()
            receiver_task.cancel()
            await ws.close()
            return
        await asyncio.sleep(0.1)


async def ws_sender(ws):
    while True:
        if len(send_queue) > 0:
            m = send_queue.popleft()
            await ws.send(m)

        await asyncio.sleep(0.1)


async def ws_receiver(ws):
    run_after_update = False
    code_uploading = False
    while True:
        m = await ws.recv()

        if m[0] == ord(WS_EXPERIMENT_UPLOAD_START):
            run_after_update = state == STATE_RUNNING
            event_stop_experiment.clear()
            await event_stop_experiment.wait()
            f = open("experiment.py", "wb")
            send_queue.append(WS_EXPERIMENT_UPLOAD_CONTINUE)
            code_uploading = True
        if m[0] == ord(WS_EXPERIMENT_UPLOAD_CODE):
            f.write(m[1:])
            send_queue.append(WS_EXPERIMENT_UPLOAD_CONTINUE)
        if m[0] == ord(WS_EXPERIMENT_UPLOAD_END):
            f.close()
            update_experiment_hash()
            if run_after_update:
                event_start_experiment.clear()
            code_uploading = False
        if m[0] == ord(WS_RESET):
            machine.reset()
        if m[0] == ord(WS_EXPERIMENT_STOP) and state == STATE_RUNNING:
            event_stop_experiment.clear()
        if m[0] == ord(WS_EXPERIMENT_START) and state != STATE_RUNNING:
            if code_uploading:
                run_after_update = True
            else:
                event_start_experiment.clear()
        if m[0] == ord(WS_RENAME):
            persistent_state["name"] = m[1:]
            save_persistent_state()
            machine.reset()


async def status_led_driver():
    led = neopixel.NeoPixel(machine.Pin(PIN_LED_STATUS), 1)

    while True:
        led.fill(state_colors[state])
        led.write()
        await asyncio.sleep(net_state_timings[net_state][0])
        led.fill((0, 0, 0))
        led.write()
        await asyncio.sleep(net_state_timings[net_state][1])


async def experiment_wrapper():
    # reimport the experiment
    if "experiment" in sys.modules:
        del sys.modules["experiment"]

    try:
        from experiment import run
    except Exception as e:
        return e

    robot = Robot()
    await robot.init()

    try:
        await run(robot)
    except asyncio.CancelledError:
        # reinit to stop any motors and leds
        await robot.stop()
    except Exception as e:
        return e


async def main():
    global state

    asyncio.create_task(status_led_driver())

    try:
        os.stat(persistent_state_file_path)
    except OSError:
        save_persistent_state()

    load_persistent_state()

    if persistent_state["running"]:
        experiment_task = asyncio.create_task(experiment_wrapper())
        state = STATE_RUNNING
    else:
        # dummy task, so below code doesn't crash if it is told to stop
        class DummyTask:
            def cancel(self):
                pass

            def done(self):
                return False

        experiment_task = DummyTask()
        robot = Robot()
        await robot.init()
        await robot.stop()
        state = STATE_STOPPED

    ws_task = asyncio.create_task(ws_handler())

    last_telemetry = 0

    while True:
        if not event_stop_experiment.is_set():
            experiment_task.cancel()
            event_stop_experiment.set()
            state = STATE_STOPPED
            save_persistent_state()

        if not event_start_experiment.is_set():
            experiment_task.cancel()
            experiment_task = asyncio.create_task(experiment_wrapper())
            event_start_experiment.set()
            state = STATE_RUNNING
            save_persistent_state()

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
            save_persistent_state()

        if ws_task.done():
            ws_task = asyncio.create_task(ws_handler())

        if last_telemetry + 5 < time.time():
            send_queue.append(
                WS_TELEMETRY + struct.pack("16sB", experiment_hash, state)
            )
            last_telemetry = time.time()

        await asyncio.sleep(0.1)


asyncio.run(main())
