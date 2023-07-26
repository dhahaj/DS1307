# DS1307 RTC Library

This library provides a Python interface to the DS1307 real-time clock (RTC) chip over I2C. It uses the Telemetrix library to communicate with the RTC. The DS1307 RTC is a low-power, full binary-coded decimal (BCD) clock/calendar with 56 bytes of NV SRAM. Address and data are transferred serially through an I2C, bidirectional bus.

## Installation

To install the library, you can download the source code from this repository and then install it using pip:

```
pip install .
```

## Usage

Here is an example of how to use the library:

```python
from ds1307 import DS1307

# Initialize the RTC
rtc = DS1307(port='COM3')

# Set the time
rtc.adjust(datetime(2022, 1, 1, 12, 0, 0))

# Get the time
print(rtc.get_date())
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.
