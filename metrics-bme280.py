#!/usr/bin/env python3

import time

import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)
data = bme280.sample(bus, address, calibration_params)

ts = time.time()
print("sensor.temperature {} {:.0f}".format(((data.temperature * 9 / 5) + 32), ts ))
print("sensor.pressure {} {:.0f}".format(data.pressure, ts))
print("sensor.humidity {} {:.0f}".format(data.humidity, ts))
