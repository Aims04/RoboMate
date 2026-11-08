#Note from Aiman: This is a Experimental file for hardware intial tests, not the production or final file!!
#For the oled production level file go to oled_display.py
import time
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

def stable_test():
    try:
        # Use a very basic init
        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial)
        
        print("Stabilizing power...")
        # Clear screen first
        device.clear()
        time.sleep(1)

        for i in range(5):
            print(f"Cycle {i+1}: Testing screen refresh...")
            with canvas(device) as draw:
                # Just draw one tiny dot to keep power draw low
                draw.point((0, 0), fill="white")
                draw.text((20, 20), f"TEST OK: {i}", fill="white")
            time.sleep(2)
            
        print("Test complete. If it didn't glitch, your wiring is likely too long or I2C speed was too high.")

    except Exception as e:
        print(f"Hardware Error: {e}")

if __name__ == "__main__":
    stable_test()

