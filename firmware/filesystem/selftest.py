import time
import struct
import machine
import neopixel
from hardware import (
    Bumpers,
    LEDs,
    PIN_COLOR_SENSOR_LEFT_SDA,
    PIN_COLOR_SENSOR_LEFT_SCL,
    PIN_COLOR_SENSOR_RIGHT_SDA,
    PIN_COLOR_SENSOR_RIGHT_SCL,
    PIN_LED_COMS,
    PIN_LED_STATUS,
)


def selftest(skip_wait=False):
    bumpers = Bumpers()
    coms = neopixel.NeoPixel(machine.Pin(PIN_LED_COMS), 1)
    status = neopixel.NeoPixel(machine.Pin(PIN_LED_STATUS), 1)
    i2c_left = machine.SoftI2C(
        freq=250000, sda=PIN_COLOR_SENSOR_LEFT_SDA, scl=PIN_COLOR_SENSOR_LEFT_SCL
    )
    i2c_right = machine.SoftI2C(
        freq=250000, sda=PIN_COLOR_SENSOR_RIGHT_SDA, scl=PIN_COLOR_SENSOR_RIGHT_SCL
    )
    fail = False

    coms.fill((32, 32, 0))
    coms.write()
    status.fill((0, 0, 0))
    status.write()

    # detect color sensors
    if i2c_left.scan() != [16]:
        print("SELFTEST: Left color sensor not found")
        fail = True
    else:
        # init left sensor
        i2c_left.writeto_mem(16, 0, b"\x00\x00")

    if i2c_right.scan() != [16]:
        print("SELFTEST: Right color sensor not found")
        fail = True
    else:
        # init right sensor
        i2c_right.writeto_mem(16, 0, b"\x00\x00")

    # check reasonable default ADC values
    if not 1e6 < (res := bumpers.adc_front.read_uv()) < 2.7e6:
        print("SELFTEST: Front bumper ADC not at middle, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_back.read_uv()) < 2.7e6:
        print("SELFTEST: Back bumper ADC not at middle, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_left.read_uv()) < 2.7e6:
        print("SELFTEST: Left bumper ADC not at middle, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_right.read_uv()) < 2.7e6:
        print("SELFTEST: Right bumper ADC not at middle, value:", res)
        fail = True

    # check that bumpers react correctly and aren't shorted with each other
    # front
    bumpers.pin_front.init(mode=machine.Pin.OUT)
    bumpers.pin_front.value(False)

    time.sleep(0.1)

    if not (res := bumpers.adc_front.read_uv()) < 1e6:
        print("SELFTEST: Front bumper not detecting being driven low, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_back.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Back bumper reacts to front bumper being driven low, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_left.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Left bumper reacts to front bumper being driven low, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_right.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Right bumper reacts to front bumper being driven low, value:",
            res,
        )
        fail = True

    bumpers.pin_front.value(True)

    time.sleep(0.1)

    if not (res := bumpers.adc_front.read_uv()) > 2.7e6:
        print("SELFTEST: Front bumper not detecting being driven high, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_back.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Back bumper reacts to front bumper being driven high, value:",
            res,
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_left.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Left bumper reacts to front bumper being driven high, value:",
            res,
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_right.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Right bumper reacts to front bumper being driven high, value:",
            res,
        )
        fail = True

    bumpers.pin_front.init(mode=machine.Pin.IN)

    # back
    bumpers.pin_back.init(mode=machine.Pin.OUT)
    bumpers.pin_back.value(False)

    time.sleep(0.1)

    if not (res := bumpers.adc_back.read_uv()) < 1e6:
        print("SELFTEST: Back bumper not detecting being driven low, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_front.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Front bumper reacts to back bumper being driven low, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_left.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Left bumper reacts to back bumper being driven low, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_right.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Right bumper reacts to back bumper being driven low, value:", res
        )
        fail = True

    bumpers.pin_back.value(True)

    time.sleep(0.1)

    if not (res := bumpers.adc_back.read_uv()) > 2.7e6:
        print("SELFTEST: Back bumper not detecting being driven high, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_front.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Front bumper reacts to back bumper being driven high, value:",
            res,
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_left.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Left bumper reacts to back bumper being driven high, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_right.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Right bumper reacts to back bumper being driven high, value:",
            res,
        )
        fail = True

    bumpers.pin_back.init(mode=machine.Pin.IN)

    # left
    bumpers.pin_left.init(mode=machine.Pin.OUT)
    bumpers.pin_left.value(False)

    time.sleep(0.1)

    if not (res := bumpers.adc_left.read_uv()) < 1e6:
        print("SELFTEST: Left bumper not detecting being driven low, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_back.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Back bumper reacts to left bumper being driven low, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_front.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Front bumper reacts to left bumper being driven low, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_right.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Right bumper reacts to left bumper being driven low, value:", res
        )
        fail = True

    bumpers.pin_left.value(True)

    time.sleep(0.1)

    if not (res := bumpers.adc_left.read_uv()) > 2.7e6:
        print("SELFTEST: Left bumper not detecting being driven high, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_back.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Back bumper reacts to left bumper being driven high, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_front.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Front bumper reacts to left bumper being driven high, value:",
            res,
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_right.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Right bumper reacts to left bumper being driven high, value:",
            res,
        )
        fail = True

    bumpers.pin_left.init(mode=machine.Pin.IN)

    # right
    bumpers.pin_right.init(mode=machine.Pin.OUT)
    bumpers.pin_right.value(False)

    time.sleep(0.1)

    if not (res := bumpers.adc_right.read_uv()) < 1e6:
        print("SELFTEST: Right bumper not detecting being driven low, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_back.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Back bumper reacts to right bumper being driven low, value:", res
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_front.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Front bumper reacts to right bumper being driven low, value:",
            res,
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_left.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Left bumper reacts to right bumper being driven low, value:", res
        )
        fail = True

    bumpers.pin_right.value(True)

    time.sleep(0.1)

    if not (res := bumpers.adc_right.read_uv()) > 2.7e6:
        print("SELFTEST: Right bumper not detecting being driven high, value:", res)
        fail = True

    if not 1e6 < (res := bumpers.adc_back.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Back bumper reacts to right bumper being driven high, value:",
            res,
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_front.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Front bumper reacts to right bumper being driven high, value:",
            res,
        )
        fail = True

    if not 1e6 < (res := bumpers.adc_left.read_uv()) < 2.7e6:
        print(
            "SELFTEST: Left bumper reacts to right bumper being driven high, value:",
            res,
        )
        fail = True

    bumpers.pin_right.init(mode=machine.Pin.IN)

    if fail:
        coms.fill((32, 0, 0))
        coms.write()
        status.fill((32, 0, 0))
        status.write()
        print("SELFTEST: FAIL")
        return False

    print("SELFTEST: PASS")

    if skip_wait:
        return True

    for _ in range(100):
        r = struct.unpack("<H", i2c_left.readfrom_mem(16, 5, 2, addrsize=8))[0]
        g = struct.unpack("<H", i2c_left.readfrom_mem(16, 6, 2, addrsize=8))[0]
        b = struct.unpack("<H", i2c_left.readfrom_mem(16, 7, 2, addrsize=8))[0]

        coms.fill((r // 8, g // 8, b // 8))
        coms.write()

        r = struct.unpack("<H", i2c_right.readfrom_mem(16, 5, 2, addrsize=8))[0]
        g = struct.unpack("<H", i2c_right.readfrom_mem(16, 6, 2, addrsize=8))[0]
        b = struct.unpack("<H", i2c_right.readfrom_mem(16, 7, 2, addrsize=8))[0]

        status.fill((r // 8, g // 8, b // 8))
        status.write()

        time.sleep(0.1)

    coms.fill((0, 0, 0))
    coms.write()
    status.fill((0, 0, 0))
    status.write()

    return True
