import asyncio
import neopixel, machine

async def run(robot):
    for i in range(10):
        await robot.print(i)
    while True:
        await robot.leds.set_coms((0, 0, 8))
        await asyncio.sleep(0.01)
        await robot.leds.set_coms((0, 0, 0))
        await asyncio.sleep(0.01)


