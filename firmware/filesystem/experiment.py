import asyncio


async def run(robot):
    while True:
        await robot.leds.set_coms((8, 8, 8))
        await asyncio.sleep(0.01)
        await robot.leds.set_coms((0, 0, 0))
        await asyncio.sleep(0.01)
