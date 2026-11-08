#Note from Aiman: This is a Experimental file for hardware intial tests, not the production or final file!!
#For the oled production level file go to oled_display.py

import time

MODE = "screen"  # change to "oled" on Raspberry Pi

# =========================
# SCREEN MODE (TESTING)
# =========================
if MODE == "screen":
    import pygame
    pygame.init()
    WIDTH, HEIGHT = 400, 200
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Eyes")

    BLACK = (0, 0, 0)
    BLUE = (0, 150, 255)

    def draw_eyes(open=True, look="center"):
        screen.fill(BLACK)
        
        # Dimensions
        eye_w, eye_h = 70, 70
        radius = 18
        
        # Horizontal shift amount
        shift = 0
        if look == "left": shift = -25
        if look == "right": shift = 25

        # Eye Positions (Left eye centered at 120, Right at 280)
        # We apply the 'shift' to the X coordinate
        eyes = [ (120 + shift, 100), (280 + shift, 100) ]

        for pos in eyes:
            if open:
                # Rounded square
                rect = pygame.Rect(pos[0] - eye_w//2, pos[1] - eye_h//2, eye_w, eye_h)
                pygame.draw.rect(screen, BLUE, rect, border_radius=radius)
            else:
                # Blink (thin rounded line)
                blink_rect = pygame.Rect(pos[0] - eye_w//2, pos[1] - 4, eye_w, 8)
                pygame.draw.rect(screen, BLUE, blink_rect, border_radius=4)

        pygame.display.flip()

    # Animation Loop
    running = True
    sequence = ["center", "left", "center", "right"]
    step = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        current_look = sequence[step % len(sequence)]
        
        # 1. Look in a direction
        draw_eyes(open=True, look=current_look)
        time.sleep(1.5)
        
        # 2. Quick Blink
        draw_eyes(open=False, look=current_look)
        time.sleep(0.1) 
        
        step += 1

    pygame.quit()

# =========================
# OLED MODE (RASPBERRY PI)
# =========================
elif MODE == "oled":
    import board
    import busio
    from PIL import Image, ImageDraw
    import adafruit_ssd1306

    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

    width, height = oled.width, oled.height
    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)

    def draw_eyes(open=True, look="center"):
        draw.rectangle((0, 0, width, height), fill=0)
        
        shift = 0
        if look == "left": shift = -10
        if look == "right": shift = 10
        
        eye_size = 24
        radius = 8
        centers = [(40 + shift, 32), (88 + shift, 32)]

        for cx, cy in centers:
            if open:
                draw.rounded_rectangle(
                    (cx - 12, cy - 12, cx + 12, cy + 12),
                    radius=radius, fill=1
                )
            else:
                # Flat blink line
                draw.rounded_rectangle(
                    (cx - 12, cy - 2, cx + 12, cy + 2), 
                    radius=2, fill=1
                )

        oled.image(image)
        oled.show()

    while True:
        for move in ["center", "left", "center", "right"]:
            draw_eyes(open=True, look=move)
            time.sleep(2)
            draw_eyes(open=False, look=move)
            time.sleep(0.1)