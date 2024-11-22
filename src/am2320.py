#!/usr/bin/env python3

# These are needed for talking to the i2c bus
import os
import fcntl

import time


class AM2320:
    # Constructor to set up the class
    def __init__(self, device="/dev/i2c-1", i2caddr=0x5C):
        # I *think* this is about setting the address for i2c
        # slave requests in the Linux kernel (?)
        self.slave = 0x0703
        # Open the i2c bus in read/write mode as a file object
        self.fd = os.open(device, os.O_RDWR)
        fcntl.ioctl(self.fd, self.slave, i2caddr)

    def ReadTemperature(self):
        self.WakeSensor()

        os.write(self.fd, b'\x03\x02\x02')
        time.sleep(0.0001)

        raw_data = bytearray(os.read(self.fd, 6))
        if (raw_data[0] != 0x03) or (raw_data[1] != 0x02):
            print("ERROR: recieved bytes 0 and 1 corrupt")
            return None

        # CRC
        crc = CRC16(raw_data[0:4])
        if crc != ((raw_data[5] << 8) + raw_data[4]):
            print("CRC error, data corrupt!")
            return None

        return float(raw_data[2] << 8 | raw_data[3]) / 10

    def ReadHumidity(self):
        self.WakeSensor()

        os.write(self.fd, b'\x03\x00\x02')
        time.sleep(0.0001)

        raw_data = bytearray(os.read(self.fd, 6))
        if (raw_data[0] != 0x03) or (raw_data[1] != 0x02):
            print("ERROR: recieved bytes 0 and 1 corrupt")
            return None

        # CRC
        crc = CRC16(raw_data[0:4])
        if crc != ((raw_data[5] << 8) + raw_data[4]):
            print("CRC error, data corrupt!")
            return None

        return float(raw_data[2] << 8 | raw_data[3]) / 10

    def ReadTemperatureHumidity(self):
        self.WakeSensor()

        os.write(self.fd, b'\x03\x00\x04')

        time.sleep(0.0001)

        raw_data = bytearray(os.read(self.fd, 8))
        if (raw_data[0] != 0x03) or (raw_data[1] != 0x04):
            print("ERROR: recieved bytes 0 and 1 corrupt")
            return None

        # CRC
        crc = CRC16(raw_data[0:6])
        if crc != ((raw_data[7] << 8) + raw_data[6]):
            print("CRC error, data corrupt!")
            return None

        tem = float(raw_data[4] << 8 | raw_data[5]) / 10
        hum = float(raw_data[2] << 8 | raw_data[3]) / 10
        return tem, hum

    def WakeSensor(self):
        # The AM2320 drops into sleep mode when not interacted
        # with for a while.  It wakes up when poked across the i2c bus
        # but doesn't return data immediately, so poke it to wake it
        # and ignore the fact that no acknowledgement is recieved.
        while True:
            try:
                os.write(self.fd, b'\0x00')
                break
            except:
                pass


def CRC16(buf):
    # Do the Cyclic Redundancy Code (CRC) check.  This progressively combines
    # the first 6 bytes recieved (raw_data bytes 0-5) with a variable of value
    # 0xFFFF in a way which should eventually result in a value which is equal
    # to the combined CRC bytes.  If this check fails then something has been
    # corrupted during transmission.
    CRC = 0xFFFF
    for byte in buf:
        CRC = CRC ^ byte
        for x in range(0, 8):
            if CRC & 0x01 == 0x01:
                CRC = CRC >> 1
                CRC = CRC ^ 0xA001
            else:
                CRC = CRC >> 1
    return CRC
