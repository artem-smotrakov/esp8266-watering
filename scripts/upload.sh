#!/bin/bash

# upload main.py to esp8266 with mpfshell

sudo mpfshell \
    -n -c \
    "open ttyUSB0; put main.conf; put src/weather.py; put src/pump.py; \
    put src/main.py; put src/util.py; put src/config.py; put src/http.py"
