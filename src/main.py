# ssid and password for the access point
# make sure that the password is not too short
# otherwise, an OSError occurs while setting up a wi-fi access point
ACCESS_POINT_SSID = 'esp8266-watering'
ACCESS_POINT_PASSWORD = 'helloesp8266'

class WeatherHandler:

    def __init__(self, key):
        self.key = key

        print('try out the key')
        from rsa import pkcs1
        pkcs1.sign(b'message', self.key, 'SHA-256')

    def handle(self, t, h):
        print('temperature = %.2f' % t)
        print('humidity    = %.2f' % h)

# entry point
from weather import Weather
from pump import Pumps
from config import Config
from machine import Pin
import util
import time
import gc

# enable garbage collection
gc.enable()
print('garbage collection threshold: ' + str(gc.threshold()))

# load a config from a file
config = Config('main.conf', 'key.json')

# initialize the pumps and the switch which turns them on and off
pumps = Pumps(config.get('first_pump_pin'), config.get('second_pump_pin'),
              config.get('pump_switch_pin'),
              config.get('watering_interval'), config.get('watering_duration'))

weather_handler = WeatherHandler(config.private_rsa_key())

# initialize the DHT22 sensor which measures temperature and humidity
weather = Weather(config.get('dht22_pin'),
                  config.get('measurement_interval'),
                  weather_handler)

# initilize the switch which enables the configuration mode
# if the switch changes its state, then the board is going to reboot immediately
# in order to turn on/off the configuration mode
config_mode_switch = Pin(config.get('config_mode_switch_pin'), Pin.IN)
config_mode_switch.irq(lambda pin: util.reboot())

# first, check if the configuration mode is enabled
# if so, set up an access point, and then start an HTTP server
# the server provides a web form which updates the configuraion of the device
# the server runs on http://192.168.4.1:80
if config_mode_switch.value() == 1:
    from http import HttpServer
    from settings import ConnectionHandler
    print('enabled configuration mode')
    access_point = util.start_access_point(ACCESS_POINT_SSID, ACCESS_POINT_PASSWORD)
    handler = ConnectionHandler(config)
    ip = access_point.ifconfig()[0]
    HttpServer(ip, 80, handler).start()
    util.reboot()

# try to connect to wi-fi if the configuraion mode is disabled
util.connect_to_wifi(config.get('ssid'), config.get('password'))

# then, start the main loop
# in the loop, the board is going to check temperature and humidity
# and also turn on the pumps according to the schedule specified by a user
while True:
    weather.check()
    pumps.check()
    time.sleep(1) # in seconds
