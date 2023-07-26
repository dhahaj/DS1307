"""
This module provides a Python interface to the DS1307 real-time clock (RTC) over I2C.
It uses the Telemetrix library to communicate with the RTC.

The DS1307 RTC is a low-power, full binary-coded decimal (BCD) clock/calendar with 56 bytes of NV SRAM.
Address and data are transferred serially through an I2C, bidirectional bus.

This module provides methods to read and write the date and time from the RTC, as well as utility methods
to convert between decimal and BCD (Binary-Coded Decimal) values.
"""

from telemetrix import telemetrix
from datetime import datetime
import time
import sys


class DS1307:
    """
    DS1307 RTC class

    This class is used to interface with the DS1307 RTC.

    Attributes:
        DS1307_RAM_ADDR: The starting address of the DS1307's RAM.
        DS1307_ADDRESS: The I2C address of the DS1307.
        SEC_REG: The address of the seconds register.
        MIN_REG: The address of the minutes register.
        HOUR_REG: The address of the hours register.
        DOW_REG: The address of the day of the week register.
        DOM_REG: The address of the day of the month register.
        MONTH_REG: The address of the month register.
        YEAR_REG: The address of the year register.
    """

    DS1307_RAM_ADDR = 0x08
    DS1307_ADDRESS = 0x68
    SEC_REG = 0x00
    MIN_REG = 0x01
    HOUR_REG = 0x02
    DOW_REG = 0x03
    DOM_REG = 0x04
    MONTH_REG = 0x05
    YEAR_REG = 0x06

    def __init__(self, port=None):
        """
        Initialize the DS1307 RTC.

        Args:
            port (str, optional): The COM port to use for communication. Defaults to None.
        """
        self.board = telemetrix.Telemetrix(com_port=port)
        self.board.set_pin_mode_i2c()
        time.sleep(0.1) 

        self.date = None
        self.start_time = None

    def get_date(self):
        """
        Get the date from the RTC.

        Returns:
            datetime: The current date and time as a datetime object.
        """
        return self.date

    def request_time(self):
        """
        Get the time from the RTC.

        This method sends a request to the RTC to read the time and date.
        The actual time and date are processed in the process_data method.
        """
        self.board.i2c_read(self.DS1307_ADDRESS, 0x00, 7, self.process_data)

    def write_time(self, hours, minutes, seconds):
        """
        Write the time to the RTC.

        Args:
            hours (int): The hours to set, in 24-hour format.
            minutes (int): The minutes to set.
            seconds (int): The seconds to set.
        """
        self.board.i2c_write(
            self.DS1307_ADDRESS, [self.SEC_REG, self.dec_to_bcd(seconds)]
        )
        self.board.i2c_write(
            self.DS1307_ADDRESS, [self.MIN_REG, self.dec_to_bcd(minutes)]
        )
        self.board.i2c_write(
            self.DS1307_ADDRESS, [self.HOUR_REG, self.dec_to_bcd(hours)]
        )

    def write_date(self, day, month, year):
        """
        Write the date to the RTC.

        Args:
            day (int): The day of the month to set.
            month (int): The month to set.
            year (int): The year to set, in YYYY format.
        """
        self.board.i2c_write(self.DS1307_ADDRESS, [self.DOM_REG, self.dec_to_bcd(day)])
        self.board.i2c_write(
            self.DS1307_ADDRESS, [self.MONTH_REG, self.dec_to_bcd(month)]
        )
        # Note: DS1307 expects the year in the format 00-99 (not 1900-2099). Convert appropriately.
        self.board.i2c_write(
            self.DS1307_ADDRESS, [self.YEAR_REG, self.dec_to_bcd(year % 100)]
        )

    def bcd_to_dec(self, bcd_val):
        """
        Convert a BCD value to a decimal value.

        Args:
            bcd_val (int): The BCD value to convert.

        Returns:
            int: The decimal equivalent of the BCD value.
        """
        return ((bcd_val & 0xF0) >> 4) * 10 + (bcd_val & 0x0F)

    def dec_to_bcd(self, dec):
        """
        Convert a decimal value to a BCD value.

        Args:
            dec (int): The decimal value to convert.

        Returns:
            int: The BCD equivalent of the decimal value.
        """
        tens, units = divmod(dec, 10)
        return (tens << 4) + units

    def process_data(self, data, time_stamp=None):
        """
        Process the data returned from the RTC.

        This method is called when data is received from the RTC.
        It unpacks the data and updates the date attribute.

        Args:
            data (list): The data received from the RTC.
            time_stamp (float, optional): The time the data was received. Defaults to None.
        """
        # Unpack data
        (
            i2c_command,
            i2c_port,
            num_bytes,
            i2c_addr,
            i2c_register,
            seconds_bcd,
            minutes_bcd,
            hours_bcd,
            dow_bcd,
            dom_bcd,
            month_bcd,
            year_bcd,
            time_stamp,
        ) = data

        self.date = datetime(
            year=self.bcd_to_dec(year_bcd) + 2000,
            month=self.bcd_to_dec(month_bcd),
            day=self.bcd_to_dec(dom_bcd),
            hour=self.bcd_to_dec(hours_bcd),
            minute=self.bcd_to_dec(minutes_bcd),
            second=self.bcd_to_dec(seconds_bcd),
            microsecond=0,
            tzinfo=None,
        )

        if self.start_time is None:
            self.start_time = self.date

    def adjust(self, dt):
        """
        Adjust the RTC to the given datetime.

        Args:
            dt (datetime): The datetime to set the RTC to.
        """
        day = dt.day
        month = dt.month
        year = dt.year
        hours = dt.hour
        minutes = dt.minute
        seconds = dt.second

        self.write_date(day, month, year)
        self.write_time(hours, minutes, seconds)

    def close(self):
        """
        Close the connection to the board.

        This method should be called when you are done using the RTC.
        """
        self.board.shutdown()
