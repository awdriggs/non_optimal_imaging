# Single Pixel Camera
A "camera" that captures a single color value.

![one pixel camera](/imgs/sp-combined.png)

The device uses a multispectral light sensor to capture visual light when a button is pressed. The multispectral data is converted to an RGB value and displayed on a single RGB led.
Buttons are used to review the captured colors and to clear the output.

Currently, there is no way to capture the colors from the device and they are deleted whenever the device is turned off.

## Components
- [Raspberry Pi Pico V1](https://www.raspberrypi.com/products/raspberry-pi-pico/)
- [Adafruit AS 7341 Multispectral Sensor](https://www.adafruit.com/product/4698)
- A Single [Neopixel](https://www.adafruit.com/product/1904)
- Three push buttons
- 3.3v LiPo battery
- [Adafruit Micro-Lipo Charger](https://www.adafruit.com/product/1904)

## Circuit
![breadboarded circuit](/imgs/sp-0.png)

- Neopixel data to GP12
- Capture button to GP13
- Play button to GP14
- Clear button to GP15
- Sensor SCL to GP17
- Sensor SDA to GP16
