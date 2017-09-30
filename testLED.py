from bibliopixel.led import *
from bibliopixel.drivers.APA102 import *
import time

driver = DriverAPA102(60, use_py_spi = True, c_order = ChannelOrder.BGR, SPISpeed = 16)
led = LEDStrip(driver, masterBrightness = 64)

rep = 0
timer = 0

hsv = [0, 255, 255]

while True: #for i in range(0, 10000):
	led.fillHSV(tuple(hsv), 0, 60)
	led.update()
	hsv[0] = (hsv[0] + 1) % 255
	time.sleep(0.05)

	'''
	temp = time.time()
	tuple = (0,0,0)
	if rep % 3 == 0:
		tuple = (255, 0, 0)
	if rep % 3 == 1:
		tuple = (0, 255, 0)
	if rep % 3 == 2:
		tuple = (0, 0, 255)
	buffer = []
	for x in range(0, led.numLEDs):
		buffer += tuple
	led.setBuffer(buffer)
	led.update()
	timer += time.time() - temp
	rep += 1
	'''

timer /= rep
print "%.20f" % timer
