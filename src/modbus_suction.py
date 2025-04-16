from pymodbus.client import ModbusSerialClient as ModbusClient
import logging
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np


class Modbus_suction:
    def __init__(self, port='COM6', baudrate=38400, parity='E', timeout=1):
        self.client = ModbusClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            timeout=timeout
        )
        self.connect = self.client.connect()

    def __del__(self):
        # Shut down the motor
        self.suction_off()
        time.sleep(1)
        self.client.close()

    def suction_on(self):
        """
        Turn on the suction
        Returns:
        """
        a = self.client.write_coil(0, 1)
        print("Suction is on")
        time.sleep(1)

    def suction_off(self):
        """
        Turn on the suction
        Returns:
        """
        a = self.client.write_coil(0, 0)
        print("Suction is off")
        time.sleep(1)


if __name__ == '__main__':
    motor = Modbus_suction()

    motor.suction_on()
    print("Suction is on")

    motor.suction_off()
