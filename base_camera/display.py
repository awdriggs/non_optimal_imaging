import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

class DisplayController:
    def __init__(self):
        # === Pin Setup ===
        spi = board.SPI()
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D20)
        reset_pin = digitalio.DigitalInOut(board.D21)

        # === Display Config ===
        self.disp = st7789.ST7789(
            spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            width=135,
            height=240,
            rotation=270,
            x_offset=53,
            y_offset=40,
            baudrate=24000000
        )

        # Adjust logical display dimensions
        self.width = self.disp.height
        self.height = self.disp.width

        self.blank_image = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))

        # === Backlight Control ===
        self.backlight = digitalio.DigitalInOut(board.D16)
        self.backlight.direction = digitalio.Direction.OUTPUT
        self.backlight.value = False  # Start with display off

    # def show_image(self, image: Image.Image):
    #     if image.size != (self.width, self.height):
    #         image = image.resize((self.width, self.height))
    #     self.disp.image(image)

    def show_image(self, image: Image.Image, overlay_text=None):
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))

        if overlay_text:
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("/home/awdriggs/fonts/Quicksand-Regular.ttf", 16)
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), overlay_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (self.width - text_width) // 2
            y = self.height - text_height - 5  # 5px from bottom

            draw.text((x, y), overlay_text, fill=(255, 0, 0), font=font)

        self.disp.image(image)

    def clear(self):
        self.disp.image(self.blank_image)

    def set_backlight(self, state: bool):
        self.backlight.value = state

    def get_dimensions(self):
        return (self.width, self.height)

    def get_blank_image(self):
        return self.blank_image

