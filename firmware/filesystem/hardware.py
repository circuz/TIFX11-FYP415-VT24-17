import machine
import _thread
import time
import struct
import neopixel
import asyncio

PIN_COLOR_SENSOR_LEFT_SDA = const(25)
PIN_COLOR_SENSOR_LEFT_SCL = const(4)
PIN_COLOR_SENSOR_RIGHT_SDA = const(14)
PIN_COLOR_SENSOR_RIGHT_SCL = const(26)

PIN_BUMPER_FRONT = const(35)
PIN_BUMPER_BACK = const(36)
PIN_BUMPER_LEFT = const(33)
PIN_BUMPER_RIGHT = const(39)

PIN_BUMPER_DRIVE_FRONT = const(21)
PIN_BUMPER_DRIVE_BACK = const(23)
PIN_BUMPER_DRIVE_LEFT = const(19)
PIN_BUMPER_DRIVE_RIGHT = const(22)

PIN_MOTOR_LEFT = const(16)
PIN_MOTOR_RIGHT = const(27)

PIN_LED_COMS = const(13)
PIN_LED_STATUS = const(32)

WS_EXPERIMENT_MESSAGE = const(b"\x0c")


class ColorSensors:
    left = (0, 0, 0)
    right = (0, 0, 0)

    task = None

    def __init__(self):
        self.i2c_left = machine.SoftI2C(
            freq=250000, sda=PIN_COLOR_SENSOR_LEFT_SDA, scl=PIN_COLOR_SENSOR_LEFT_SCL
        )
        self.i2c_right = machine.SoftI2C(
            freq=250000, sda=PIN_COLOR_SENSOR_RIGHT_SDA, scl=PIN_COLOR_SENSOR_RIGHT_SCL
        )
        # enable sensor
        self.i2c_left.writeto_mem(16, 0, b"\x00\x00")
        self.i2c_right.writeto_mem(16, 0, b"\x00\x00")
        self.task = asyncio.create_task(self.update())

    async def update(self):
        while True:
            self.left = (
                struct.unpack("<H", self.i2c_left.readfrom_mem(16, 5, 2, addrsize=8))[
                    0
                ],
                struct.unpack("<H", self.i2c_left.readfrom_mem(16, 6, 2, addrsize=8))[
                    0
                ],
                struct.unpack("<H", self.i2c_left.readfrom_mem(16, 7, 2, addrsize=8))[
                    0
                ],
            )
            self.right = (
                struct.unpack("<H", self.i2c_right.readfrom_mem(16, 5, 2, addrsize=8))[
                    0
                ],
                struct.unpack("<H", self.i2c_right.readfrom_mem(16, 6, 2, addrsize=8))[
                    0
                ],
                struct.unpack("<H", self.i2c_right.readfrom_mem(16, 7, 2, addrsize=8))[
                    0
                ],
            )
            await asyncio.sleep(0.1)


class Bumpers:
    # Tri state, False = pulled low, True = pulled high
    front = None
    back = None
    left = None
    right = None

    # also tri state
    drive_front = None
    drive_back = None
    drive_left = None
    drive_right = None

    task = None

    def __init__(self):
        self.pin_front = machine.Pin(PIN_BUMPER_DRIVE_FRONT, machine.Pin.IN)
        self.pin_back = machine.Pin(PIN_BUMPER_DRIVE_BACK, machine.Pin.IN)
        self.pin_left = machine.Pin(PIN_BUMPER_DRIVE_LEFT, machine.Pin.IN)
        self.pin_right = machine.Pin(PIN_BUMPER_DRIVE_RIGHT, machine.Pin.IN)
        self.adc_front = machine.ADC(PIN_BUMPER_FRONT, atten=machine.ADC.ATTN_11DB)
        self.adc_back = machine.ADC(PIN_BUMPER_BACK, atten=machine.ADC.ATTN_11DB)
        self.adc_left = machine.ADC(PIN_BUMPER_LEFT, atten=machine.ADC.ATTN_11DB)
        self.adc_right = machine.ADC(PIN_BUMPER_RIGHT, atten=machine.ADC.ATTN_11DB)
        self.task = asyncio.create_task(self.update())

    async def update(self):
        while True:

            # stop driving pins
            self.pin_front.init(mode=machine.Pin.IN)
            self.pin_back.init(mode=machine.Pin.IN)
            self.pin_left.init(mode=machine.Pin.IN)
            self.pin_right.init(mode=machine.Pin.IN)

            await asyncio.sleep(0.05)

            # get pin values
            self.front = (
                None if 1e6 < (val := self.adc_front.read_uv()) < 2.7e6 else val > 1.5e6
            )
            self.back = (
                None if 1e6 < (val := self.adc_back.read_uv()) < 2.7e6 else val > 1.5e6
            )
            self.left = (
                None if 1e6 < (val := self.adc_left.read_uv()) < 2.7e6 else val > 1.5e6
            )
            self.right = (
                None if 1e6 < (val := self.adc_right.read_uv()) < 2.7e6 else val > 1.5e6
            )

            # start driving pins again
            if self.drive_front is not None:
                self.pin_front.init(mode=machine.Pin.OUT)
                self.pin_front.value(False)

            if self.drive_back is not None:
                self.pin_back.init(mode=machine.Pin.OUT)
                self.pin_back.value(False)

            if self.drive_left is not None:
                self.pin_left.init(mode=machine.Pin.OUT)
                self.pin_left.value(False)

            if self.drive_right is not None:
                self.pin_right.init(mode=machine.Pin.OUT)
                self.pin_right.value(False)

            await asyncio.sleep(0.1)


class Motors:
    def __init__(self):
        self.pwm_left = machine.PWM(machine.Pin(PIN_MOTOR_LEFT), freq=1000, duty=0)
        self.pwm_right = machine.PWM(machine.Pin(PIN_MOTOR_RIGHT), freq=1000, duty=0)

    async def set_left(self, value):
        if not 0 <= value <= 1:
            raise ValueError("Motor value must be in range 0-1")
        self.pwm_left.duty(
            int(value * 1024 * 0.5)
        )  # motors are rated for 1.6V, they shouldn't get 100% 3.3V

    async def set_right(self, value):
        if not 0 <= value <= 1:
            raise ValueError("Motor value must be in range 0-1")
        self.pwm_right.duty(int(value * 1024 * 0.5))

    async def stop(self):
        await self.set_left(0)
        await self.set_right(0)

    async def go_forward(self):
        await self.set_left(1)
        await self.set_right(1)

    async def go_left(self):
        await self.set_left(0)
        await self.set_right(1)

    async def go_right(self):
        await self.set_left(1)
        await self.set_right(0)


class LEDs:
    coms = (0, 0, 0)

    def __init__(self):
        self.coms = neopixel.NeoPixel(machine.Pin(PIN_LED_COMS), 1)

    async def clear(self):
        await self.set_coms((0, 0, 0))

    async def set_coms(self, value):
        self.coms.fill(value)
        self.coms.write()


class Robot:
    def __init__(self, send_queue, name):
        self.color_sensors = ColorSensors()
        self.bumpers = Bumpers()
        self.motors = Motors()
        self.leds = LEDs()

        self.send_queue = send_queue
        self.name = name

    async def init(self):
        await self.leds.clear()

    async def stop(self):
        if self.bumpers.task:
            self.bumpers.task.cancel()
        if self.color_sensors.task:
            self.color_sensors.task.cancel()

        await self.motors.stop()
        await self.leds.clear()

    async def print(self, string):
        self.send_queue.append(WS_EXPERIMENT_MESSAGE + str(string).encode())
