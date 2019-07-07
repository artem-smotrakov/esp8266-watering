#!/bin/bash

# upload main.py to esp8266 with mpfshell
mpfshell \
    -n -c \
    "open ttyUSB0; \
    put main.conf; lcd src; mput .*\.py; \
    md http; cd http; lcd http; mput .*\.py;"
