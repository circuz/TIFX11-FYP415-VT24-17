import asyncio

async def run(robot):
    while True:
        await robot.leds.set_coms((0,32,0))
        await asyncio.sleep(1)
        await robot.leds.set_coms((0,0,0))
        await asyncio.sleep(1)
        
        # await robot.motors.go_forward()
        # await asyncio.sleep(1)
        # await robot.motors.go_left()
        # await asyncio.sleep(1)
        # await robot.motors.go_right()
        # await asyncio.sleep(1)
        # await robot.motors.stop()
        await asyncio.sleep(0.1)
    # await asyncio.sleep(1)
        
