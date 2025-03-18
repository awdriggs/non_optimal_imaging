import time
import board
import digitalio

class Button:
    def __init__(self, pin):
        self.button = digitalio.DigitalInOut(pin)
        self.button.switch_to_input(pull=digitalio.Pull.DOWN)
        self.previous_state = False  # Stores the last state

    def is_pressed(self):
        """Returns True if button is currently pressed."""
        return self.button.value

    def is_released(self):
        """Returns True only when the button is released after being pressed."""
        current_state = self.button.value
        if not current_state and self.previous_state:
            self.previous_state = current_state
            return True
        self.previous_state = current_state
        return False


# Define buttons on different pins
capture = Button(board.GP13)
play = Button(board.GP14)
clear = Button(board.GP15)

while True:
    if capture.is_released():
        print("capture Released")
    
    if play.is_released():
        print("play Released")
    
    if clear.is_released():
        print("clear  Released")

    time.sleep(0.05)  # Small debounce delay
