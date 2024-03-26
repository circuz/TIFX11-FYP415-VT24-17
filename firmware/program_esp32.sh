set -e

esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ~/Downloads/ESP32_GENERIC-OTA-20240105-v1.22.1.bin
echo RESET!!!
echo RESET!!!
echo RESET!!!
echo RESET!!!
echo RESET!!!
sleep 10
stty -F /dev/ttyUSB0 115200
cat init.py | sed "s/\$/$(printf '\r')/" > /dev/ttyUSB0
