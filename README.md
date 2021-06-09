# SafePi
SafePi is a Python based tracking tool for Safemoon, aimed to be run on a Raspberry Pi with GPIO displays. It connects to gate.io and pulls your Safemoon balance from BscScan.

![alt text](https://github.com/aCallum/SafePi/blob/main/safepi.jpg)

## Support Me

Thanks for checking out SafePi. It would be great to have your support in any way possible. Crypto donations, or a coffee to keep me coding are always welcome!

BTC Donations Welcome: 3Fy8MVbx35zMrBnTP6rJt1Cb7fwS4NacvA

Or buy me a coffee: https://ko-fi.com/aCallum

### Prerequisites:
This project was built using a Waveshare OLED Display which uses the SSD1306 drivers in Python. It is possible to run on other OLED displays (eg Adafruit), but you will need to locate and integrate the device specific drivers manually.

1. Almost any RaspberryPi (with GPIO support):
    - https://thepihut.com/collections/raspberry-pi/products/raspberry-pi-zero-wh-with-pre-soldered-header
2. A SPI/I2C GPIO display (Using the SSD1306 Device Driver):
    - https://thepihut.com/collections/raspberry-pi-screens/products/128x32-2-23inch-oled-display-hat-for-raspberry-pi
3. SD Card 8GB or higher -- image it with Raspberry Pi OS Lite
4. Power Cable & Charger/Battery Bank

### Build the Device:
1. Burn the OS in SD Card with Raspberry Pi Imager
    - https://www.raspberrypi.org/software/
2. Connect the display to Pi GPIO Pins
3. Plug in Power
4. Install OS
5. Enable SPI in Raspi Config
    - sudo raspi-config
    - select Interface Options > SPI > Yes
6. Reboot the Pi
    - sudo reboot now

### Software & Install:
1. Get a BscScan API Key
    - https://bscscan.com/myapikey
2. Get your Safemoon Wallet Address (via Trust Wallet/Pancake Swap)
3. Install Python3, Git, and SPI
    - sudo apt-get update
    - sudo apt-get install python3-pip
    - sudo apt-get install python3-pil
    - sudo apt-get install python3-numpy
    - sudo pip3 install RPi.GPIO
    - sudo pip3 install spidev
    - sudo pip3 install ccxt
    - sudo pip3 install schedule
    - sudo apt-get install git
4. clone this project to RaspberryPi
    - git clone https://github.com/aCallum/SafePi
5. Edit config.py in nano or other text editor and add your keys from BscScan API
    - nano SafePi/config.py
    - or open with text editor
    - Then fill in the API Key and Safemoon Wallet Address
    - Leave the Safemoon Contract Address as default

### Run
1. Change to project folder
    - cd SafePi
2. Run it with Python3 
    - sudo python3 main.py

### Support Me

Thanks for checking out SafePi. It would be great to have your support in any way possible. Crypto donations, or a coffee to keep me coding are always welcome!

BTC Donations Welcome: 3Fy8MVbx35zMrBnTP6rJt1Cb7fwS4NacvA

Or buy me a coffee: https://ko-fi.com/aCallum
