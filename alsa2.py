import alsaaudio as aa
from os import listdir
import decoder
import numpy as np
from scipy.fftpack import rfft, irfft
import sys
import time
import thread
from display import *

queue = []
data = ""
chunk = 1024
song = ""
curSong = ""
skip = False
pause = False
startHue = 0.5
prev = 0
maxVol = 1
prevHue = startHue
Hue = 0.0
history = [0, 0]
minmax = [0, 1]

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
		print data
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

	#hue = 1.0 * np.argmax(fft) / len(fft)
	if np.argmax(fft) != 0:
		hue = 1.0 * np.log10(np.argmax(fft)) / np.log10(len(fft))
	else:
		hue = 0.0
	hue += startHue
	hue = prevHue + (hue - prevHue) * np.absolute(hue - prevHue) * 0.5
	prevHue = hue
	
	'''
	print "inverse fft"
	for i in range(1, 4):
		fft[i] *= .1
	clean = irfft(fft)
	'''

	cur = (np.average(np.absolute(both)))
	if cur <= 0:
		cur = 1

	cur = np.log10(cur) ** 2

	minmax.append(cur)

	if len(minmax) > 70:#44100 / chunk:
		minmax.pop(0)

	minVol = min(minmax)
	maxVol = max(max(minmax), 1)
	showVal = (cur - minVol) / (maxVol - minVol)
	prev = prev + (showVal - prev) * 1 if showVal > prev else prev - (prev - showVal) * .15
	#show(prev, hue)
	show(history[0], history[1])
	history = [prev, hue]
	#print(showVal)
	time.sleep(chunk / 44100.0)
print "escaped analysis loop"
