#!/bin/bash

# upload to esp8266 with mpfshell

sudo mpfshell \
    -n -c \
    "open ttyUSB0; put main.conf; put key.json; \
    lcd src; mput .*\.py; md rsa; cd rsa; lcd rsa; mput .*\.py;"
