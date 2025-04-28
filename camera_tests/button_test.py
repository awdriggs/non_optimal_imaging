from gpiozero import Button
from signal import pause

# button = Button(17, bounce_time=0.1)
button = Button(26, bounce_time=0.1)
# button = Button(14)

def pushed():
    print("Button pressed")


button.when_pressed = pushed

print("ready")
pause()

