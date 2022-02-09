#!/usr/bin/python

import board
import neopixel

led_size = 60

with neopixel.NeoPixel(board.D21, led_size, auto_write=False) as pixels:
  cur = 0
  while True:
    pixels[cur] = (0, 0, 0)
    cur = (cur + 1) % led_size
    pixels[cur] = (0, 0, 255)
    pixels.show()
