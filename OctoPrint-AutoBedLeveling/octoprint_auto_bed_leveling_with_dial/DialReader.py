#!/bin/env python3
from smbus2 import SMBus, i2c_msg
from bitstring import BitArray, Bits, pack
from contextlib import contextmanager
import RPi.GPIO as GPIO

DIAL_ADDRESS            = 0x32
READ_SENSOR_CMD         = 0x01
READY_PIN               =4

GPIO.setmode(GPIO.BCM)
GPIO.setup(READY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin to be an input pin and set initial value to be pulled low (off)


class Dial:
    def __init__(self, bus_id=1, address=DIAL_ADDRESS):
        self.i2c=SMBus(bus_id)
        self.addr=address

    def read(self):
        self.i2c.write_byte(self.addr, READ_SENSOR_CMD)
        ret=GPIO.wait_for_edge(READY_PIN, GPIO.FALLING,  timeout=5000)
        if ret is None:
            raise TimeoutError
        msg=i2c_msg.read(self.addr, 2)
        self.i2c.i2c_rdwr(msg)
        return(int.from_bytes(msg, byteorder='little', signed=True))



if __name__=="__main__":
    import sys
    from time import sleep
    dial=Dial()
 
    for i in range(10):
        print("Read Dial: %.2fmm" % (dial.read()/100))