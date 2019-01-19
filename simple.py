#!/usr/bin/env python

import time

# For the display
import luma.core.interface.serial
import luma.oled.device
import luma.core.render
from PIL import ImageFont

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

font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 18)

while True:
    data = bme280.sample(bus, address, calibration_params)

    with luma.core.render.canvas(display_device) as canvas:
        canvas.text((0, 15), '{:.2f} degF'.format((data.temperature * 9 / 5) + 32), fill="white", font=font)
        canvas.text((0, 35), '{:.2f}% rH'.format(data.humidity), fill="white", font=font)

    time.sleep( 1 )
