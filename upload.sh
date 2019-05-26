#!/bin/bash

# upload main.py to esp8266 with mpfshell

sudo mpfshell \
    -n -c \
    "open ttyUSB0; put main.conf; put weather.py; put pump.py; put main.py; \
        put util.py; put config.py; put https.py"
