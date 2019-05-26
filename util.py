from machine import Pin
import time
import machine
import network

# reboot the board after some delay
def reboot(delay = 5):
    print('rebooting ...')
    time.sleep(delay)
    machine.reset()

# start wifi access point
def start_access_point(ssid, password):
    access_point = network.WLAN(network.AP_IF)
    access_point.active(True)
    access_point.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)
    return access_point

# tries to connect to wi-fi
# returns true in case of successful connection
def connect_to_wifi(ssid, password):
    if not config:
        print('config is empty')
        return

    if not config['ssid'] or not config['password']:
        print('could not find ssid/password in config file')
        return False

    # try to connect
    print('connecting to network: %s' % ssid)
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    nic.connect(ssid, password)

    # wait some time
    attempt = 0
    while attempt < 11 and not nic.isconnected():
        print('connecting ...')
        time.sleep(1.0)
        attempt = attempt + 1

    if nic.isconnected():
        print('connected')
        return True
    else:
        print('connection failed')
        return False

# returns true if a switch on the specified pin is on
def is_switch_on(pin_number):
    pin = Pin(pin_number, Pin.IN)
    return True if pin.value() == 1 else False

def string_to_millis(string):
    print("debug: string_to_millis: " + string)
    if not string:
        return 0
    value = 0
    for item in string.split(' '):
        item = item.strip()
        l = len(item)
        n = int(item[:l - 1])
        m = item[l - 1]
        if m == 'd':
            value = value + n * 24 * 60 * 60 * 1000
        if m == 'h':
            value = value + n * 60 * 60 * 1000
        if m == 'm':
            value = value + n * 60 * 1000
        if m == 's':
            value = value + n * 1000

    return value
