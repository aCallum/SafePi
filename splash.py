import config
import time
import numpy as np
import subprocess

if config.RUN_EMULATOR:
    import cv2
else:
    import sys
    sys.path.append('./drivers')
    import SPI
    import SSD1305

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops

if config.RUN_EMULATOR:
    imageEncoding = 'RGB'
else:
    imageEncoding = '1'
    # Raspberry Pi pin configuration:
    RST = None     # on the PiOLED this pin isnt used
    # Note the following are only used with SPI:
    DC = 24
    SPI_PORT = 0
    SPI_DEVICE = 0

    # 128x32 display with hardware SPI:
    disp = SSD1305.SSD1305_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
    # Initialize library.
    disp.begin()
    # Clear display.
    disp.clear()
    disp.display()  

frameSize = (128, 32)
titleFont = ImageFont.truetype("fonts/04B_03__.TTF", 8)
startTime = time.time()

while (time.time() - startTime) < 10:

    canvas = Image.new(imageEncoding, (frameSize))
    image = Image.open('images/safe_logo.bmp').convert(imageEncoding)
    image = image.resize((32, 32), Image.ANTIALIAS)
    canvas.paste(image, (64-16,0))

    if config.RUN_EMULATOR:
        # Virtual display
        npImage = np.asarray(canvas)
        frameBGR = cv2.cvtColor(npImage, cv2.COLOR_RGB2BGR)
        cv2.imshow('HashAPI', frameBGR)
        k = cv2.waitKey(16) & 0xFF
        if k == 27:
            break
    else:
        # Hardware display
        disp.image(canvas)
        disp.display()
        time.sleep(1./60)

if config.RUN_EMULATOR:
    # Virtual display
    cv2.destroyAllWindows()
else:
    cmd = "hostname -I | cut -d\' \' -f1"
    ip = str(subprocess.check_output(cmd, shell = True)).replace("b'"," ").replace("\\n'", "")
    draw = ImageDraw.Draw(canvas)
    draw.text((-1, 25), str(ip), fill='white', font=titleFont)
    disp.image(canvas)
    disp.display()