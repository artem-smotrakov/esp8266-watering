#!/bin/bash

# flash esp8266 with specified firmware

sudo python -m esptool \
  --port /dev/ttyUSB0 \
  --baud 460800 write_flash \
  --flash_size=detect 0 esp8266-20190125-v1.10.bin
