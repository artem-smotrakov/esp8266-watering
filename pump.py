from machine import Pin

class Pumps:

    def __init__(self, first_pump_pin, second_pump_pin, switch_pin):
        self.first_pump = Pin(first_pump_pin, Pin.OUT)
        self.second_pump = Pin(second_pump_pin, Pin.OUT)
        self.switch_pin = Pin(switch_pin, Pin.IN)
        self.turn_off()
        self.status = 0

    def turn_off(self):
        self.first_pump.off()
        self.second_pump.off()

    def turn_on(self):
        self.first_pump.on()
        self.second_pump.on()

    def check(self):
        new_status = self.switch_pin.value()
        if self.status != new_status:
            self.turn_on() if new_status == 1 else self.turn_off()
            self.status = new_status
