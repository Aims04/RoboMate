#Note from Aiman: This is the production/ready file to exe, whereas the other 3 oled displays are experimental files for testing.
from luma.core.interface.serial import i2c 
from luma.core.render import canvas
from luma.oled.device import sh1106
import time

class OLEDDisplay:
    def __init__(self, port=1, address=0x3C):
        self.serial = i2c(port=port, address=address)
        self.device = sh1106(self.serial)
        self.device.clear()

    def draw_eyes(self, offset_x=0, blink=False):
        with canvas(self.device) as d:
            if blink:
                d.rounded_rectangle((20+offset_x, 30, 50+offset_x, 34), radius=5, fill="white")
                d.rounded_rectangle((78+offset_x, 30, 108+offset_x, 34), radius=5, fill="white")
            else:
                d.rounded_rectangle((20+offset_x, 20, 50+offset_x, 50), radius=8, fill="white")
                d.rounded_rectangle((78+offset_x, 20, 108+offset_x, 50), radius=8, fill="white")

    def blink(self, offset_x=0):
        self.draw_eyes(offset_x)
        time.sleep(0.12)
        self.draw_eyes(offset_x, True)
        time.sleep(0.08)
        self.draw_eyes(offset_x)
        time.sleep(0.12)


# ?? MAIN LOOP (NO GAPS VERSION)
if __name__ == "__main__":
    time.sleep(2)

    display = OLEDDisplay()
    start = time.time()

    while True:
        try:
            # ?? ORIGINAL NICE MOVEMENT (VISIBLE SHIFT)
            display.blink(0)     # center
            display.blink(5)     # right
            display.blink(0)     # center
            display.blink(-5)    # left

            # ?? silent refresh BEFORE freeze
            if time.time() - start > 5:
                display = OLEDDisplay()   # reinit instantly
                start = time.time()

        except Exception:
            # fast recovery (no delay)
            display = OLEDDisplay()
