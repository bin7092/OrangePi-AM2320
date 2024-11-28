# SPDX-FileCopyrightText: 2016 Mike Causer <https://github.com/mcauser>
# SPDX-License-Identifier: MIT

"""
MicroPython Aosong AM2320 I2C driver
https://github.com/mcauser/micropython-am2320

Prints the temperature and humidity
"""
import sys
import time

sys.path.append("..")
from src import am2320

sensor = am2320.AM2320()

for x in range(0, 10):
   print(f"Temperature: {sensor.ReadTemperature()} C")
   print(f"Humidity: {sensor.ReadHumidity()} RH")
   for x in sensor.ReadTemperatureHumidity():
      print(x)
   print("\n")
   time.sleep(0.5)
