# button_test.py

from gpiozero import Button
from signal import pause

# Define buttons
buttons = {
    "Capture (GPIO4)": Button(4),
    "Preview (GPIO12)": Button(12),
    "Playback (GPIO23)": Button(23),
    "Forward (GPIO18)": Button(18),
    "Back (GPIO25)": Button(25),
    "Share (GPIO26)": Button(26),
    "Up (GPIO1)": Button(1),
    "Down (GPIO24)": Button(24),
    "Extra1 (GPIO17)": Button(17),
    "Extra2 (GPIO27)": Button(27),
    "Extra3 (GPIO22)": Button(22),
    "Extra4 (GPIO2)": Button(2),
}

# Attach handlers
for name, button in buttons.items():
    button.when_pressed = lambda n=name: print(f"🔵 {n} pressed")
    button.when_released = lambda n=name: print(f"⚪ {n} released")

print("🧪 Button Test: Press buttons to see output.")
pause()

