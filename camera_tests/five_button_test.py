from gpiozero import Button
from signal import pause

# Create Button objects for each GPIO pin
buttons = {
    1: Button(1),
    25: Button(25),
    24: Button(24),
    23: Button(23),
    18: Button(18),
}

# Define a function to run when a button is pressed
def make_callback(pin):
    return lambda: print(f"Button on GPIO {pin} pressed")

# Attach the callback to each button's `when_pressed` event
for pin, button in buttons.items():
    button.when_pressed = make_callback(pin)

print("Listening for button presses... (Ctrl+C to exit)")
pause()

