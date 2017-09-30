from bibliopixel.led import *
from bibliopixel.drivers.APA102 import *

driver = DriverAPA102(60, use_py_spi = True, c_order = ChannelOrder.BGR, SPISpeed = 16)
led = LEDStrip(driver, masterBrightness = 128)

def show(size, color):
	while color > 1.0:
		color -= 1.0
	if size < .08:
		size = .08
	if size > 1.0:
		size = 1.0
	'''
	buffer = []
	dead = []
	tuple = (0, 0, 255)
	count = 0
	lit = size * 30
	while count < lit:
		buffer += tuple
		count += 1
	while count < 30:
		dead += (0,0,0)
		count += 1
	buffer = dead + buffer + buffer + dead
	led.setBuffer(buffer)
	'''
	filled = 60 * size
	dead = 60 - filled
	led.fillHSV((0,0,0), 0, int(dead / 2))
	led.fillHSV((int(color * 255), 255, 255), int(dead / 2), int(60 - dead / 2))
	led.fillHSV((0,0,0), int(60 - dead / 2), 60)
	led.update()

def shutdown():
	led.fillHSV((0,0,0), 0, 60)
	led.update()
