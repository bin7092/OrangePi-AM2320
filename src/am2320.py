# SPDX-FileCopyrightText: 2016 Mike Causer <https://github.com/mcauser>
# SPDX-License-Identifier: MIT

"""
MicroPython Aosong AM2320 I2C driver
https://github.com/mcauser/micropython-am2320
"""

import wiringpi


def sleep_ms(time):  # ms
    wiringpi.delay(time)


def _crc16(buf):
    crc = 0xFFFF
    for c in buf:
        crc ^= c
        for _ in range(8):
            if crc & 0x01:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


class AM2320:
    def __init__(self, device="/dev/i2c-1", i2caddr=0x5C):
        wiringpi.wiringPiSetup()
        self.i2caddr = i2caddr
        self._i2c = wiringpi.wiringPiI2CSetupInterface(device, i2caddr)

    def i2c_write_byte(self, byte):
        if wiringpi.wiringPiI2CWriteReg8(self._i2c, self.i2caddr, byte) < 0:
            print("Error write byte from AM2320")
            raise IOError("I2C write failed")
        return 0

    def i2c_read_byte(self, reg):
        byte = wiringpi.wiringPiI2CReadReg8(self._i2c, reg)
        if byte < 0:
            print("Error read byte from AM2320")
            return -1
        return byte

    def ReadTemperature(self):
        self.WakeSensor()
        while True:
            try:
                self.i2c_write_byte(0x03)
                self.i2c_write_byte(0x02)
                self.i2c_write_byte(0x02)
                break
            except IOError:
                pass
        sleep_ms(15)
        high = self.i2c_read_byte(0x02)
        low = self.i2c_read_byte(0x03)
        temperature = float(high << 8 | low) / 10
        return temperature

    def ReadHumidity(self):
        self.WakeSensor()
        while True:
            try:
                self.i2c_write_byte(0x03)
                self.i2c_write_byte(0x00)
                self.i2c_write_byte(0x02)
                break
            except IOError:
                pass
        sleep_ms(15)
        high = self.i2c_read_byte(0x02)
        low = self.i2c_read_byte(0x03)
        humidity = float(high << 8 | low) / 10
        return humidity

    def ReadTemperatureHumidity(self):
        self.WakeSensor()
        while True:
            try:
                self.i2c_write_byte(0x03)
                self.i2c_write_byte(0x00)
                self.i2c_write_byte(0x04)
                break
            except IOError:
                pass
        sleep_ms(15)
        a = self.i2c_read_byte(0x00)
        b = self.i2c_read_byte(0x01)
        highHum = self.i2c_read_byte(0x02)
        lowHum = self.i2c_read_byte(0x03)
        highTem = self.i2c_read_byte(0x04)
        lowTem = self.i2c_read_byte(0x05)
        crc = self.i2c_read_byte(0x06)

        c = b << 8 | a
        hum = highHum << 8 | lowHum
        tem = highTem << 8 | lowTem
        d = crc | tem << 8 | hum << 24
        if c != _crc16(d):
            raise ValueError("Checksum error")
        humidity = float(hum) / 10
        temperature = float(tem) / 10
        return temperature, humidity

    def WakeSensor(self):
        while True:
            try:
                self.i2c_write_byte(0x00)
                break
            except IOError:
                pass
        sleep_ms(3)
