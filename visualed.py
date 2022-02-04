#!/usr/bin/python

import alsaaudio as aa
import board
import colorsys
import math
import neopixel
import numpy as np
from scipy.fftpack import rfft
import time

chunk = 1024
max_vol = 2.0**15
led_size = 44
mid = led_size // 2
num_mel_bands = led_size // 2
freq_granularity = 5
max_mel_freq = 500

inStream = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, device='hw:0,1')
inStream.setrate(44100)
inStream.setformat(aa.PCM_FORMAT_S32_BE)
inStream.setperiodsize(chunk)

old_linspace = np.linspace(0, 1, chunk)
new_linspace = np.linspace(0, 1, 22000 // freq_granularity)

hi = [1 for i in range(30)]
cur_frame = 0

past = [0.0 for i in range(num_mel_bands)]

boost = 0

hue = 0.0

def mel2hz(mel_freq):
  return int(700 * (10 ** (mel_freq / 2595.0) - 1))

with neopixel.NeoPixel(board.D21, 60, auto_write=False) as pixels:
  while True:
    data = list(inStream.read())[1]
    raw = np.frombuffer(data, dtype=np.int16)
    sound = [int(raw[i * 2]) + int(raw[i * 2 + 1]) for i in range(len(raw) // 2)]
    sound = [x / max_vol for x in sound]
    
    print(sum(sound))
  
    fft = rfft(sound)
    # fft with chunk # of buckets from (44100/chunk)hz to 22khz
    fft = np.absolute(fft)
    # fft with 22000/freq_granularity # of buckets in same range
    fft = np.interp(new_linspace, old_linspace, fft)

    hi[cur_frame] = max(max(fft), 1)
    cur_frame = (cur_frame + 1) % len(hi)

    for i in range(num_mel_bands):
      mel_freq_lo = i * max_mel_freq / num_mel_bands
      mel_freq_hi = (i + 1) * max_mel_freq / num_mel_bands - 1
      # convert mel freq to normal freq
      freq_lo = mel2hz(mel_freq_lo)
      freq_hi = mel2hz(mel_freq_hi)
      # scale down normal freq to bucket size for lookup
      #freq_lo = (freq_lo - 44100 // chunk) // freq_granularity
      #freq_hi = (freq_hi - 44100 // chunk) // freq_granularity
      freq_lo = freq_lo // freq_granularity
      freq_hi = freq_hi // freq_granularity
      # bounds checks
      freq_lo = max(min(freq_lo, len(fft) - 1), 0)
      freq_hi = max(min(freq_hi, len(fft) - 1), 1)

      disp = fft[freq_lo:freq_hi]
      disp = np.average(disp) / max(hi)
      # cut out noise
      disp = disp if (disp > 0.3 or past[i] > 0.3) else 0

      '''
      if i == 0:
        boost = 1 if disp > 0.5 else 0
      else:
        disp += 0.2 * (num_mel_bands - i) / num_mel_bands if boost else 0.0
      '''
      
      disp = min(1.0, disp)

      # Handle decay
      diff = disp - past[i]
      if diff > 0:
        disp = past[i] + diff * 0.7
      else:
        disp = past[i] + diff * 0.2
      past[i] = disp

      rgb = colorsys.hsv_to_rgb(hue, 1, 1)
      rgb = tuple([int(256 * x * disp) for x in rgb])
      pixels[mid + i + 16] = rgb
      pixels[mid - i - 1 + 16] = rgb
    hue = (hue + 0.0005) % 1.0
    pixels.show()
