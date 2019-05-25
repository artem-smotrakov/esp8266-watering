#!/bin/bash

# verify flashed firmware on esp8266

sudo python -m esptool \
  --port /dev/ttyUSB0 \
  --baud 460800 verify_flash \
  --flash_size=detect 0 esp8266-20190125-v1.10.bin
