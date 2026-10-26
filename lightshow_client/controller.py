import neopixel
import board
import math
import time
import random

class Controller:

    def __init__(self, pixels: int):
        self.NUM = pixels
        self.pixels = neopixel.NeoPixel(board.D18, pixels, brightness=1, auto_write=False, pixel_order=neopixel.GRB)

        self.frame = 0
        self.program = ['fill', {'color': (255,0,0)}]

        self.time = time.perf_counter()

        self.running = True
    
    #data = (command, {arg: value, ...})
    def run_command(self, data):
        self.program = data
        self.frame = 0
    
    def stop(self):
        self.running = False
        self.pixels.fill((0, 0, 0))
        self.pixels.show()  

    def run(self):
        while self.running:
            now = time.perf_counter()
            if now - self.time >= (1/60):
                call = getattr(self, self.program[0])
                call(self.program[1], self.frame)
                self.pixels.show()
                self.frame += 1
                
                self.time = time.perf_counter()
    
    #//programs
    #color
    def fill(self, args, frame):
        ##set defaults to protect against network corruption
        color = args.get('color', (0,0,0))

        self.pixels.fill(color)
    
    #start_point: 1 = top, -1 = bottom
    #length, start_point, middle, start (color), end, speedmod
    def trail(self, args, frame):
        speedmod = args.get('speedmod', 1)
        start_point = args.get('start_point', 1)
        length = args.get('length', 15)
        middle = args.get('middle', False)
        start = args.get('start', (0,255,0))
        end = args.get('end', (255,0,0))

        if frame % speedmod == 0:
            self.pixels.fill((0,0,0))

            color_offsets = [0,0,0]
            for i in range(3):
                color_offsets[i] = math.floor((end[i] - start[i]) / length)

            for pixel in range(length):
                set_color = (max(start[0] + (color_offsets[0] * pixel), 0), max(start[1] + (color_offsets[1] * pixel), 0), max(start[2] + (color_offsets[2] * pixel), 0))
                if middle:
                    self.pixels[int(((((-(frame / speedmod) * start_point) + pixel) % round(self.NUM / 2))))] = set_color
                    self.pixels[int((((((frame / speedmod) * start_point) - pixel) % round(self.NUM / 2))) + round(self.NUM / 2))] = set_color
                else:
                    self.pixels[int((((((frame / speedmod) * start_point) + pixel) % round(self.NUM / 2))))] = set_color
                    self.pixels[int(((((((frame / speedmod) * start_point) + pixel) % round(self.NUM / 2)))) + round(self.NUM / 2))] =  set_color

    ##helper function, not something to call
    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos*3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos*3)
            g = 0
            b = int(pos*3)
        else:
            pos -= 170
            r = 0
            g = int(pos*3)
            b = int(255 - pos*3)
        return (g, r, b)

    #I did not write this command, Mr. Eversole (a former teacher with experience with these LEDs) provided it to me
    def rainbow_cycle(self, args, frame):
        for i in range(self.NUM):
            pixel_index = (i * 256 // self.NUM) + ((frame + 1) % 255)
            self.pixels[i] = self.wheel(pixel_index & 255)

    #color, fadespeed
    def sparkle(self, args, frame):
        color = args.get('color', (255,255,255))
        fadespeed = args.get('fadespeed', 3)

        if frame % 2 == 0:
            for pixel in range(self.NUM):
                g = max(self.pixels[pixel][0] - fadespeed, 0)
                r = max(self.pixels[pixel][1] - fadespeed, 0)
                b = max(self.pixels[pixel][2] - fadespeed, 0)

                self.pixels[pixel] = (g, r, b)

            new_pixel = random.randint(1, self.NUM - 1)
            self.pixels[new_pixel] = color

    #color1, color2
    def stagger(self, args, frame):
        color1 = args.get('color1', (0,255,0))
        color2 = args.get('color2', (0,0,255))

        self.pixels.fill((0,0,0))

        for pixel in range(self.NUM):
            if -1 < (pixel % 10) < 5:
                if -1 < (frame % 20) < 9:
                    self.pixels[pixel] = color1
                else:
                    self.pixels[pixel] = color2
            else:
                if -1 < (frame % 20) < 9:
                    self.pixels[pixel] = color1
                else:
                    self.pixels[pixel] = color2

    #color
    def flash_seq(self, args, frame):
        color = args.get('color', (0,0,255))

        if frame == 0:
            toggle = bool(round(frame) % 2)
            self.pixels.fill((0,0,0))
            if toggle:
                for pixel in range(round(self.NUM / 2)):
                    self.pixels[pixel] = color
            else:
                for pixel in range(round(self.NUM / 2)):
                    self.pixels[pixel + round(self.NUM / 2)] = color
    
    # color, speed (1–10)
    def breathe(self, args, frame):
        color = args.get('color', (0,0,255))
        speed = args.get('speed', 5)

        # oscillate a brightness waveform 0 → 255 → 0
        wave = (math.sin(frame / speed) + 1) / 2
        brightness = int(wave * 255)

        r = int(color[0] * brightness / 255)
        g = int(color[1] * brightness / 255)
        b = int(color[2] * brightness / 255)

        self.pixels.fill((g, r, b))
        
    # color, speed
    def color_wipe(self, args, frame):
        color = args.get('color', (0,0,255))
        speed = args.get('speed', 5)

        index = (frame // speed) % self.NUM

        # clear the strip
        self.pixels.fill((0,0,0))

        # fill from start up to index
        for i in range(index):
            self.pixels[i] = color
    
    # color1, color2, speed
    def dual_chase(self, args, frame):
        color1 = args.get('color1', (0,0,255))
        color2 = args.get('color2', (0,255,0))
        speed = args.get('speed', 5)

        self.pixels.fill((0,0,0))

        pos1 = (frame // speed) % self.NUM
        pos2 = (self.NUM - pos1 - 1) % self.NUM

        self.pixels[pos1] = color1
        self.pixels[pos2] = color2
    
    # intensity (20–80 recommended)
    # Claude mainly wrote this function, I simply adapted it to fit into my architecture.
    def fire(self, args, frame):
        intensity = args.get('intensity', 50)

        if frame % 3 != 0:
            return

        for i in range(self.NUM):
            flicker = random.randint(-intensity, intensity)

            target_r = max(min(255, 255 - flicker), 0)
            target_g = max(min(150, 150 - flicker), 0)
            target_b = max(min(50, 50 - flicker), 0)

            # Smoothly blend current pixel → target pixel
            r = int(self.pixels[i][1] * 0.7 + target_r * 0.3)
            g = int(self.pixels[i][0] * 0.7 + target_g * 0.3)
            b = int(self.pixels[i][2] * 0.7 + target_b * 0.3)

            self.pixels[i] = (g, r, b)
    
    #speed (1), size (5), color1, color 2
    # Claude mainly wrote this function, I simply adapted it to fit into my architecture.
    def candy_cane(self, args, frame):
        speed = args.get('speed', 1)
        size = args.get('size', 5)
        color1 = args.get('color1', (255,0,0))
        color2 = args.get('color2', (0,255,0))

        if frame % 4 == 0:
            for i in range(self.NUM):
                v = (i + frame * speed) // size
                if v % 2 == 0:
                    self.pixels[i] = color1
                else:
                    self.pixels[i] = color2
    
    #speed (10), color
    # Claude mainly wrote this function, I simply adapted it to fit into my architecture.
    def star_glow(self, args, frame):
        speed = args.get('speed', 10)
        color = args.get('color', (255,0,0))

        for i in range(self.NUM):
            distance = abs(i - 49)  # around top
            wave = (math.sin(frame / speed - distance * 0.2) + 1) / 2
            bri = int(wave * 255)

            g = int(color[0] * bri / 255)
            r = int(color[1] * bri / 255)
            b = int(color[2] * bri / 255)

            self.pixels[i] = (g, r, b)
    
    #speed (4), color
    # Claude mainly wrote this function, I simply adapted it to fit into my architecture.
    def snowfall(self, args, frame):
        speed = args.get('speed', 4)
        color = args.get('color', (255,255,0))

        # fade trail
        for i in range(self.NUM):
            g = max(self.pixels[i][0] - 10, 0)
            r = max(self.pixels[i][1] - 10, 0)
            b = max(self.pixels[i][2] - 10, 0)
            self.pixels[i] = (g, r, b)

        # drop flake at random top pixel of each side
        if frame % speed == 0:
            tops = [49, 50]   # split center
            for t in tops:
                p = t + random.randint(-2, 2)  # slight randomness
                p = max(0, min(self.NUM - 1, p))
                self.pixels[p] = color
    
    #speed (30), color
    # Claude mainly wrote this function, I simply adapted it to fit into my architecture.
    def aurora(self, args, frame):
        speed = args.get('speed', 30)
        color = args.get('color', (0,255,0))

        for i in range(self.NUM):
            wave = math.sin((i / 10) + frame / speed)
            wave2 = math.sin((i / 15) - frame / (speed * 1.5))
            bri = (wave + wave2 + 2) / 4  # 0–1

            g = int(color[0] * bri)
            r = int(color[1] * bri)
            b = int(color[2] * bri)

            self.pixels[i] = (g, r, b)
