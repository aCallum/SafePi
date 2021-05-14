#coding=utf-8
from __future__ import division
import logging
import time

import I2C
import SPI
import GPIO

# Constants
SSD1305_I2C_ADDRESS = 0x3C    # 011110+SA0+RW - 0x3C or 0x3D
SSD1305_SETCONTRAST = 0x81
SSD1305_DISPLAYALLON_RESUME = 0xA4
SSD1305_DISPLAYALLON = 0xA5
SSD1305_NORMALDISPLAY = 0xA6
SSD1305_INVERTDISPLAY = 0xA7
SSD1305_DISPLAYOFF = 0xAE
SSD1305_DISPLAYON = 0xAF
SSD1305_SETDISPLAYOFFSET = 0xD3
SSD1305_SETCOMPINS = 0xDA
SSD1305_SETVCOMDETECT = 0xDB
SSD1305_SETDISPLAYCLOCKDIV = 0xD5
SSD1305_SETPRECHARGE = 0xD9
SSD1305_SETMULTIPLEX = 0xA8
SSD1305_SETLOWCOLUMN = 0x00
SSD1305_SETHIGHCOLUMN = 0x10
SSD1305_SETSTARTLINE = 0x40
SSD1305_MEMORYMODE = 0x20
SSD1305_COLUMNADDR = 0x21
SSD1305_PAGEADDR = 0x22
SSD1305_COMSCANINC = 0xC0
SSD1305_COMSCANDEC = 0xC8
SSD1305_SEGREMAP = 0xA0
SSD1305_CHARGEPUMP = 0x8D
SSD1305_EXTERNALVCC = 0x1
SSD1305_SWITCHCAPVCC = 0x2

# Scrolling constants
SSD1305_ACTIVATE_SCROLL = 0x2F
SSD1305_DEACTIVATE_SCROLL = 0x2E
SSD1305_SET_VERTICAL_SCROLL_AREA = 0xA3
SSD1305_RIGHT_HORIZONTAL_SCROLL = 0x26
SSD1305_LEFT_HORIZONTAL_SCROLL = 0x27
SSD1305_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
SSD1305_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL = 0x2A


class SSD1305Base(object):
    """Base class for SSD1305-based OLED displays.  Implementors should subclass
    and provide an implementation for the _initialize function.
    """

    def __init__(self, width, height, rst, dc=None, sclk=None, din=None, cs=None,
                 gpio=None, spi=None, i2c_bus=None, i2c_address=SSD1305_I2C_ADDRESS,
                 i2c=None):
        self._log = logging.getLogger('Adafruit_SSD1305.SSD1305Base')
        self._spi = None
        self._i2c = None
        self.width = width
        self.height = height
        self._pages = 4
        self._buffer = [0]*(width*self._pages)
        # Default to platform GPIO if not provided.
        self._gpio = gpio
        if self._gpio is None:
            self._gpio = GPIO.get_platform_gpio()
        # Setup reset pin.
        self._rst = rst
        if not self._rst is None:
            self._gpio.setup(self._rst, GPIO.OUT)
        # Handle hardware SPI
        if spi is not None:
            self._log.debug('Using hardware SPI')
            self._spi = spi
            self._spi.set_clock_hz(8000000)
        # Handle software SPI
        elif sclk is not None and din is not None and cs is not None:
            self._log.debug('Using software SPI')
            self._spi = SPI.BitBang(self._gpio, sclk, din, None, cs)
        # Handle hardware I2C
        elif i2c is not None:
            self._log.debug('Using hardware I2C with custom I2C provider.')
            self._i2c = i2c.get_i2c_device(i2c_address)
        else:
            self._log.debug('Using hardware I2C with platform I2C provider.')
            import Adafruit_GPIO.I2C as I2C
            if i2c_bus is None:
                self._i2c = I2C.get_i2c_device(i2c_address)
            else:
                self._i2c = I2C.get_i2c_device(i2c_address, busnum=i2c_bus)
        # Initialize DC pin if using SPI.
        if self._spi is not None:
            if dc is None:
                raise ValueError('DC pin must be provided when using SPI.')
            self._dc = dc
            self._gpio.setup(self._dc, GPIO.OUT)

    def _initialize(self):
        raise NotImplementedError

    def command(self,c):
        """Send self.command byte to display."""
        if self._spi is not None:
            # SPI write.
            self._gpio.set_low(self._dc)
            self._spi.write([c])
        else:
            # I2C write.
            control = 0x00   # Co = 0, DC = 0
            self._i2c.write8(control, c)

    def data(self, c):
        """Send byte of data to display."""
        if self._spi is not None:
            # SPI write.
            self._gpio.set_high(self._dc)
            self._spi.write([c])
        else:
            # I2C write.
            control = 0x40   # Co = 0, DC = 0
            self._i2c.write8(control, c)

    def begin(self, vccstate=SSD1305_SWITCHCAPVCC):
        """Initialize display."""
        # Save vcc state.
        self._vccstate = vccstate
        # Reset and initialize display.
        self.reset()
        self._initialize()
        # Turn on the display.
        self.command(SSD1305_DISPLAYON)

    def reset(self):
        """Reset the display."""
        if self._rst is None:
            return
        # Set reset high for a millisecond.
        self._gpio.set_high(self._rst)
        time.sleep(0.001)
        # Set reset low for 10 milliseconds.
        self._gpio.set_low(self._rst)
        time.sleep(0.010)
        # Set reset high again.
        self._gpio.set_high(self._rst)

    def display(self):
        # """Write display buffer to physical display."""
        for page in range(0,4):
            self.command(0xb0 + page)
            self.command(0x04)
            self.command(0x10)
            self._gpio.set_high(self._dc)
            for num in range(0,128):
                self._spi.write([self._buffer[page*128+num]])
        #         pass
    def image(self, image):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size.
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
                .format(self.width, self.height))
        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        # Iterate through the memory pages
        index = 0
        for page in range(self._pages):
            # Iterate through all x axis columns.
            for x in range(self.width):
                # Set the bits for the column of pixels at the current position.
                bits = 0
                # Don't use range here as it's a bit slow
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    bits = bits << 1
                    bits |= 0 if pix[(x, page*8+7-bit)] == 0 else 1
                # Update buffer byte and increment to next byte.
                self._buffer[index] = bits
                index += 1

    def clear(self):
        """Clear contents of image buffer."""
        self._buffer = [0]*(self.width*self._pages)

    def set_contrast(self, contrast):
        """Sets the contrast of the display.  Contrast should be a value between
        0 and 255."""
        if contrast < 0 or contrast > 255:
            raise ValueError('Contrast must be a value from 0 to 255 (inclusive).')
        self.self.command(SSD1305_SETCONTRAST)
        self.self.command(contrast)

    def dim(self, dim):
        """Adjusts contrast to dim the display if dim is True, otherwise sets the
        contrast to normal brightness if dim is False.
        """
        # Assume dim display.
        contrast = 0
        # Adjust contrast based on VCC if not dimming.
        if not dim:
            if self._vccstate == SSD1305_EXTERNALVCC:
                contrast = 0x9F
            else:
                contrast = 0xCF
class SSD1305_128_32(SSD1305Base):
    def __init__(self, rst, dc=None, sclk=None, din=None, cs=None, gpio=None,
                 spi=None, i2c_bus=None, i2c_address=SSD1305_I2C_ADDRESS,
                 i2c=None):
        # Call base class constructor.
        super(SSD1305_128_32, self).__init__(128, 32, rst, dc, sclk, din, cs,
                                             gpio, spi, i2c_bus, i2c_address, i2c)
    def _initialize(self):
        # 128x32 pixel specific initialization.
        self.command(0xAE)#--turn off oled panel
        self.command(0x04)#--turn off oled panel	
        self.command(0x10)#--turn off oled panel
        self.command(0x40)#---set low column address
        self.command(0x81)#---set high column address
        self.command(0x80)#--set start line address  Set Mapping RAM Display Start Line (0x00~0x3F)
        self.command(0xA1)#--set contrast control register
        self.command(0xA6)# Set SEG Output Current Brightness
        self.command(0xA8)#--Set SEG/Column Mapping     0xa0×óÓÒ·´ÖÃ 0xa1Õý³£
        self.command(0x1F)#Set COM/Row Scan Direction   0xc0ÉÏÏÂ·´ÖÃ 0xc8Õý³£
        self.command(0xC8)#--set normal display
        self.command(0xD3)#--set multiplex ratio(1 to 64)
        self.command(0x00)#--1/64 duty
        self.command(0xD5)#-set display offset	Shift Mapping RAM Counter (0x00~0x3F)
        self.command(0xF0)#-not offset
        self.command(0xd8)#--set display clock divide ratio/oscillator frequency
        self.command(0x05)#--set divide ratio, Set Clock as 100 Frames/Sec
        self.command(0xD9)#--set pre-charge period
        self.command(0xC2)#Set Pre-Charge as 15 Clocks & Discharge as 1 Clock
        self.command(0xDA)#--set com pins hardware configuration
        self.command(0x12)
        self.command(0xDB)#--set vcomh
        self.command(0x08)#Set VCOM Deselect Level
        self.command(0xAF)#-Set Page Addressing Mode (0x00/0x01/0x02)