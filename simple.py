#!/usr/bin/env python

import time

# For the display
import luma.core.interface.serial
import luma.oled.device
import luma.core.render

# For the sensor
import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

display_device = luma.oled.device.ssd1306(
    serial_interface = luma.core.interface.serial.i2c(
        port = 1, address = 0x3C
    )
)

display_device.persist = True

while True:
    data = bme280.sample(bus, address, calibration_params)

    with luma.core.render.canvas(display_device) as canvas:
        canvas.text((0, 15), '{:.2f} degF'.format((data.temperature * 9 / 5) + 32), fill="white")
        canvas.text((0, 30), '{:.2f}% rH'.format(data.humidity), fill="white")

    time.sleep( 1 )
