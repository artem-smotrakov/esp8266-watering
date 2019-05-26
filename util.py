# reboot the board after some delay
def reboot(delay = 5):
    import time
    import machine
    print('rebooting ...')
    time.sleep(delay)
    machine.reset()

# start wifi access point
def start_access_point(ssid, password):
    import network
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)

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
    import network
    import time
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
    from machine import Pin
    pin = Pin(pin_number, Pin.IN)
    return True if pin.value() == 1 else False
