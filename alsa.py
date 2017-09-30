import alsaaudio as aa
from os import listdir
import decoder
import numpy as np
from scipy.fftpack import rfft, irfft
import sys
import time
import thread
from display import *

data = ""
chunk = 1024
startHue = 0.5
prev = 0
maxVol = 1
prevHue = startHue
Hue = 0.0
history = [0, 0]
minmax = [0, 1]

def songThread():
	global data
	global queue
	global song
	global skip
	global curSong
	
	inStream = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, device='hw:1,0')
	inStream.setchannels(1)
	inStream.setrate(44100)
	inStream.setformat(aa.PCM_FORMAT_S16_LE)
	inStream.setperiodsize(chunk)

	outStream = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
	outStream.setchannels(1)
	outStream.setperiodsize(chunk)

	while True:
		data = list(inStream.read())[1]
		#outStream.write(data)
	print "escaped songThread loop"


#main
thread.start_new_thread(songThread, ())
time.sleep(.1)

with open("static") as f:
	static = np.array([float(x) for x in f.readline().split(", ")])

while True:
	Hue += .01
	raw = np.fromstring(data, dtype = np.int16)
	if len(raw) == 0:
		continue
	fft = np.subtract(rfft(raw), static)

	if np.argmax(fft) != 0:
		hue = 1.0 * np.log10(np.argmax(fft)) / np.log10(len(fft))
	else:
		hue = 0.0
	hue += startHue
	hue = prevHue + (hue - prevHue) * np.absolute(hue - prevHue) * 0.35
	prevHue = hue
	
	cur = (np.average(np.absolute(raw))) - 235 #235 is average static volume
	if cur <= 0:
		cur = 1

	cur = np.log10(cur) ** 2

	minmax.append(cur)

	if len(minmax) > 70:#44100 / chunk:
		minmax.pop(0)

	minVol = min(min(minmax), 0.5)
	minVol = min(minmax)
	maxVol = max(max(minmax), 1)
	showVal = (cur - minVol) / (maxVol - minVol)
	prev = prev + (showVal - prev) * 0.7 if showVal > prev else prev - (prev - showVal) * .15
	#show(prev, hue)
	show(history[0], history[1])
	history = [prev, hue]
	#print(showVal)
	time.sleep(chunk / 44100.0)
print "escaped analysis loop"
