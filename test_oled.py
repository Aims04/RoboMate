import time # just a testing file for oled screen display, u could do ur custom tests..
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

def test_display():
    try:
        # Initialize the hardware
        serial = i2c(port=1, address=0x3C)
        device = ssd1306(serial)
        
        print("Display initialized! Drawing a box...")
        
        # Draw a simple border and text to verify it's alive
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((30, 25), "ROBOMATE 4", fill="white")
            
        print("Success! You should see 'ROBOMATE 4' on the screen.")
        time.sleep(5)
        
    except Exception as e:
        print(f"Failed to talk to screen: {e}")

if __name__ == "__main__":
    test_display()
