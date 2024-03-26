import os
import machine
import neopixel

status = neopixel.NeoPixel(machine.Pin(32), 1)
status.fill((32, 32, 0))
status.write()

def recursive_delete(d):
    for file in os.listdir(d):
        path = d + "/" + file
        if os.stat(path)[0] & 16384: # if is dir
            recursive_delete(path)
            print("Deleting directory", path)
            os.unlink(path)
        elif path not in ["/boot.py", "/webrepl_cfg.py"]:
            print("Deleting file", path)
            os.unlink(path)


recursive_delete("")

files = $$FILES$$

for filename, data in files:
    if data is None:
        print("Creating directory", filename)
        os.mkdir(filename)
    else:
        print("Creating file", filename)
        with open(filename, "wb") as f:
            f.write(data)

print("Update done, resetting")
status.fill((0, 0, 0))
status.write()
machine.reset()
