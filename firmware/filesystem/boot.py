import network
import webrepl
import _thread


def init():
    # wifi setup
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect("botnet", "roboting")

    # webrepl setup
    webrepl.start(password="roboting")


# init in separate thread so other code can run immediately
_thread.start_new_thread(init, ())
