from machine import Pin
import time

class Pumps:

    def __init__(self, first_pump_pin, second_pump_pin, switch_pin, interval, duration):
        self.first_pump = Pin(first_pump_pin, Pin.OUT)
        self.second_pump = Pin(second_pump_pin, Pin.OUT)
        self.switch_pin = Pin(switch_pin, Pin.IN)
        self.turn_off()
        self.pump_status = 0
        self.interval = util.string_to_millis(interval)
        self.duration = util.string_to_millis(duration)
        self.watering_ended = time.ticks_ms()
        self.watering_started = 0

    def turn_off(self):
        self.pump_status = 0
        self.first_pump.off()
        self.second_pump.off()

    def turn_on(self):
        self.pump_status = 1
        self.first_pump.on()
        self.second_pump.on()

    def check(self):

        # first, check if the switch status has changed
        # if yes, turn on/off pumps accordingly
        switch_status = self.switch_pin.value()
        if self.pump_status != switch_status:
            self.pump_status = switch_status
            if self.pump_status == 1:
                self.turn_on()
            else:
                self.turn_off()
                self.last_watering = time.ticks_ms()

        # next, exit if the switch is on
        if switch_status == 1:
            return

        # then, if the pumps are off, check if it's time to turn them on
        current_time = time.ticks_ms()
        if self.pump_status == 0:
            deadline = time.ticks_add(self.watering_ended, self.interval)
            if time.ticks_diff(deadline, current_time) > 0:
                self.turn_on()
                self.watering_started = current_time
        else:
            # finally, if the pumps are on, check if it's time to turn them off
            deadline = time.ticks_add(self.watering_started, self.duration)
            if time.ticks_diff(deadline, current_time) > 0:
                self.turn_off()
                self.watering_ended = current_time
