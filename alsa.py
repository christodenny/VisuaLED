import alsaaudio as aa
from os import listdir
import decoder
import numpy as np
from scipy.fftpack import rfft, irfft
import sys
import time
import thread
from bibliopixel.led import *
from bibliopixel.drivers.APA102 import *

driver = DriverAPA102(60, use_py_spi = True, c_order = ChannelOrder.BGR, SPISpeed = 16)
led = LEDStrip(driver, masterBrightness = 128)

def show(size, color):
	while color > 1.0:
		color -= 1.0
	if size < .08:
		size = .08
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

queue = []
data = ""
chunk = 1024
song = ""
curSong = ""
skip = False
pause = False
startHue = 0.5
prev = 0
history = [0.0, 1.0]
prevHue = startHue
Hue = 0.0

def queueThread():
	global queue
	global skip
	global pause
	while True:
		command = raw_input("Enter a command (skip, add <songname>, current, remove): ")
		if command.startswith('s'): #skip cursong
			skip = True
		elif command.startswith('a'): #add song
			queue.append(command.split()[1])
		elif command.startswith('c'): #view current queue
			print ""
			print "Current song: ", curSong
			print "Queue: "
			for i in range(0, len(queue)):
				print (i + 1), queue[i]
			print ""
		elif command.startswith('r'): #remove song
			queue.pop(int(command.split()[1]) - 1)
		elif command.startswith('p'): #toggle play or pause
			pause = not pause
		elif command.startswith('n'): #play this song next
			queue.insert(0, command.split()[1])

def songThread():
	global data
	global queue
	global song
	global skip
	global curSong
	while True:
		stream = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
		while len(queue) == 0:
			time.sleep(1)
		curSong = queue.pop(0)
		song = decoder.open(curSong)
		stream.setperiodsize(chunk)
		data = song.readframes(chunk)
		while data != '':
			while pause:
				time.sleep(.1)
			if skip:
				skip = False
				break
			stream.write(data)
			data = song.readframes(chunk)
	print "escaped songThread loop"


#main
if len(sys.argv) > 1:
	queue.append(sys.argv[1])
queue.extend("music/" + f for f in listdir("./music/"))
thread.start_new_thread(queueThread, ())
thread.start_new_thread(songThread, ())
time.sleep(.1)

while True:
	Hue += .01
	raw = np.fromstring(data, dtype = np.int16)
	if len(raw) == 0:
		continue
	left = np.divide(raw[1::2], 2)
	right = np.divide(raw[0::2], 2)
	both = np.add(left, right)
	if song.getnchannels() == 1:
		fft = rfft(raw)
	else:
		fft = rfft(both)

	hue = 1.0 * np.argmax(fft) / len(fft)
	if np.argmax(fft) != 0:
		hue = 1.0 * np.log10(np.argmax(fft)) / np.log10(len(fft))
	else:
		hue = 0.0
	hue += startHue
	hue = prevHue + (hue - prevHue) * np.absolute(hue - prevHue)
	prevHue = hue
	
	'''
	print "inverse fft"
	for i in range(1, 4):
		fft[i] *= .1
	clean = irfft(fft)
	'''

	cur = 20 * (np.average(np.absolute(both)))
	if cur < 0:
		cur = 0

	history.append(cur)
	if len(history) > 44100 / chunk / 2:#:
		history.pop(0)
	
	showVal = 1.0 * (cur - min(history)) / (max(history) - min(history)) if max(history) != min(history) else 0.0
	prev = prev + (showVal - prev) * .4 if showVal > prev else prev - (prev - showVal) * .1
	show(prev, hue)
	time.sleep(chunk / 44100.0)
print "escaped analysis loop"
