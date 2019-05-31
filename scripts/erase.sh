#!/bin/bash

# erase flash

sudo python -m esptool --port /dev/ttyUSB0 erase_flash
