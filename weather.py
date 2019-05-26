import time
import dht
import machine

class Weather:

    def __init__(self, pin, interval):
        self.last_measurement = time.ticks_ms()
        self.dht22 = dht.DHT22(machine.Pin(pin))
        self.interval = interval

    # mesures temperature and humidity
    def measure(self):
        self.dht22.measure()
        t = self.dht22.temperature()
        h = self.dht22.humidity()
        print('temperature = %.2f' % t)
        print('humidity    = %.2f' % h)

    def check(self):
        current_time = time.ticks_ms()
        deadline = ticks_add(self.last_measurement, self.interval)
        if ticks_diff(deadline, current_time) > 0:
            self.measure()
            self.last_measurement = current_time
