#!/bin/bash

# upload main.py to esp8266 with mpfshell

sudo mpfshell -n -c "open ttyUSB0; put main.py"
