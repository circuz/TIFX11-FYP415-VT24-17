import asyncio
import webrepl
import network

# wifi setup
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("botnet", "roboting")

webrepl.start(password="roboting")


async def main():
    await asyncio.sleep(10)


asyncio.run(main())
