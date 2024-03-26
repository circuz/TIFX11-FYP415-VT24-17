# copy paste this code through serial to init the robot, then connect it to external power. It should connect to wifi and be ready for software upload.

f = open("boot.py", "wb")
f.write(b"import network\n")
f.write(b"import webrepl\n")
f.write(b"sta_if = network.WLAN(network.STA_IF)\n")
f.write(b"sta_if.active(True)\n")
f.write(b'sta_if.connect("botnet", "roboting")\n')
f.write(b'webrepl.start(password="roboting")\n')
f.close()
