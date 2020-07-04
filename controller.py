#!/usr/bin/env python3

import json
import time

from datetime import datetime

from simple_pid import PID

# To control the relays
from RPi import GPIO

# For the display
import luma.core.interface.serial
import luma.oled.device
import luma.core.render
from PIL import ImageFont

# For the sensor
import smbus2
import bme280


def poweron(pin):
    GPIO.output(pin, False)


def poweroff(pin):
    GPIO.output(pin, True)


def main():
    i2c_bus = smbus2.SMBus(1)
    sensor_address = 0x76
    display_address = 0x3c
    fridge_pin = 6
    humid_pin = 5

    temp_target = 52
    humid_target = 80
    tolerance = 0.25

    humid_pid = PID(
        1,
        0.1,
        0.05,
        output_limits=(0, 16),
        proportional_on_measurement=True,
    )

    # Set up the sensor
    sensor_params = bme280.load_calibration_params(
        i2c_bus,
        sensor_address,
    )

    # Set up the display
    display_device = luma.oled.device.ssd1306(
        serial_interface = luma.core.interface.serial.i2c(
            port = 1, address = display_address
        )
    )
    display_device.persist = True
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 18)
    smallfont = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 12)

    # Set up the power control
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fridge_pin, GPIO.OUT)
    GPIO.setup(humid_pin, GPIO.OUT)

    poweroff(fridge_pin)
    poweroff(humid_pin)
    fridge_on = False
    humid_on = False
    humid_ts = time.time()

    while True:
        try:
            with open('/usr/local/mehetweret/setpoints.json', 'r') as f:
                setpoints = json.load(f)
                temp_target = setpoints.get('temperature', temp_target)
                humid_target = setpoints.get('humidity', humid_target)
        except:
            pass

        humid_pid.setpoint = humid_target

        data = bme280.sample(i2c_bus, sensor_address, sensor_params)

        temp = (data.temperature * 9 / 5) + 32
        humid = data.humidity

        if (temp > temp_target + 0.3) and not fridge_on:
            print('Turning on refrigerator, trying to get to {}'.format(temp_target))
            poweron(fridge_pin)
            fridge_on = True
        elif (temp < temp_target + 0.2) and fridge_on:
            print('Turning off refrigerator')
            poweroff(fridge_pin)
            fridge_on = False

        if time.time() - humid_ts >= 15:
            humid_ts = time.time()
            pid_res = humid_pid(humid)
            print('PID result: {}'.format(pid_res))
            if (pid_res > 0) and not humid_on:
                print('Turning on humidifier')
                poweron(humid_pin)
                humid_on = True
            humid_ts_off = humid_ts + pid_res

        if humid_on and time.time() >= humid_ts_off:
            print('Turning off humidifier')
            poweroff(humid_pin)
            humid_on = False

        with luma.core.render.canvas(display_device) as canvas:
            statline = ''
            if fridge_on:
                statline = 'Cool'
            if humid_on:
                if statline:
                    statline += ' / '
                statline += 'Humidify'

            canvas.text(
                (0, 0),
                statline,
                fill='white',
                font=smallfont,
            )
            canvas.text(
                (0, 15),
                '{:.2f} degF'.format(temp),
                fill='white',
                font=font,
            )
            canvas.text(
                (0, 35),
                '{:.2f}% rH'.format(humid),
                fill='white',
                font=font,
            )

        time.sleep(1)

if __name__ == '__main__':
    main()
