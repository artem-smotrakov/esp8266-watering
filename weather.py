import time
import dht
import machine
import util

class Weather:

    def __init__(self, pin, interval):
        self.last_measurement = time.ticks_ms()
        self.dht22 = dht.DHT22(machine.Pin(pin))
        self.interval = util.string_to_millis(interval)

    # mesures temperature and humidity
    def measure(self):
        self.dht22.measure()
        t = self.dht22.temperature()
        h = self.dht22.humidity()
        print('temperature = %.2f' % t)
        print('humidity    = %.2f' % h)

    def check(self):
        current_time = time.ticks_ms()
        deadline = time.ticks_add(self.last_measurement, self.interval)
        if time.ticks_diff(deadline, current_time) > 0:
            self.measure()
            self.last_measurement = current_time
