import time
from datetime import datetime

class Program:
    def __init__(self, server, iot):
        self.server = server
        self.iot = iot

        self.frame = 0
        self.time = time.perf_counter()

        self.running = False

        #program
        #each seq will have a list of commands: [command, {arg: value}, duration (s)]

        self.ct_seq = [
            ['candy_cane', {"speed": 1, "size": 6, "color1": (0,255,0), "color2": (255,255,255)}, 50],

            ['aurora', {"speed": 6, "color": (200,20,20)}, 60],

            ['trail', {"length": 25, "start_point": -1, "middle": True, "start": (150,150,255), "end": (0,0,0), "speedmod": 2}, 80],

            ['rainbow_cycle', {}, 70],

            ['rainbow_cycle', {}, 5],
            ['fill', {'color': (0,0,0)}, 10],
            ['rainbow_cycle', {}, 5],
            ['fill', {'color': (0,0,0)}, 10],
            ['rainbow_cycle', {}, 5],
            ['fill', {'color': (0,0,0)}, 10],

            ['sparkle', {"color": (255,255,255), "fadespeed": 15}, 50],

            ['fire', {"intensity": 60}, 50],

            ['breathe', {"speed": 10, "color": (0,0,255)}, 60],
        ]

        self.st_seq = [
            ['candy_cane', {"speed": 1, "size": 6, "color1": (0,255,0), "color2": (255,255,255)}, 50],

            ['aurora', {"speed": 6, "color": (100,100,255)}, 60],

            ['trail', {"length": 25, "start_point": -1, "middle": True, "start": (150,150,255), "end": (0,0,0), "speedmod": 2}, 80],

            ['rainbow_cycle', {}, 70],

            ['fill', {'color': (0,0,0)}, 5],
            ['rainbow_cycle', {}, 5],
            ['fill', {'color': (0,0,0)}, 10],
            ['rainbow_cycle', {}, 5],
            ['fill', {'color': (0,0,0)}, 10],
            ['rainbow_cycle', {}, 5],
            ['fill', {'color': (0,0,0)}, 5],

            ['sparkle', {"color": (0,255,0), "fadespeed": 18}, 50],

            ['fire', {"intensity": 60}, 50],

            ['breathe', {"speed": 10, "color": (130,255,0)}, 60],
        ]



        self.r_seq = [
            ['candy_cane', {"speed": 1, "size": 6, "color1": (0,255,0), "color2": (255,255,255)}, 50],

            ['aurora', {"speed": 6, "color": (100,100,100)}, 60],

            ['trail', {"length": 50, "start_point": -1, "middle": False, "start": (0,0,255), "end": (255,255,255), "speedmod": 2}, 80],

            ['rainbow_cycle', {}, 70],

            ['fill', {'color': (0,0,0)}, 10],
            ['rainbow_cycle', {}, 5],
            ['fill', {'color': (0,0,0)}, 10],
            ['rainbow_cycle', {}, 5],
            ['fill', {'color': (0,0,0)}, 10],
            ['rainbow_cycle', {}, 5],

            ['sparkle', {"color": (255,255,255), "fadespeed": 20}, 50],

            ['fire', {"intensity": 60}, 50],

            ['breathe', {"speed": 14, "color": (255,255,255)}, 50],
        ]

        self.ce_seq = [
            ['rainbow_cycle', {}, 10000],
        ]

        self.b_seq = [
            ['trail', {"length": 50, "start_point": -1, "middle": False, "start": (0,0,255), "end": (255,255,255), "speedmod": 2}, 10000],
        ]

        self.n_seq = [
            ['trail', {"length": 10, "start_point": -1, "middle": False, "start": (0,0,255), "end": (255,0,0), "speedmod": 2}, 10000],
        ]


        self.program = {"CT": self.ct_seq, "ST": self.st_seq, "R": self.r_seq, "CE": self.ce_seq, "B": self.b_seq, "N": self.n_seq}

    #program_reset is set true when the CE, N, and B sequences should be reset
    def start(self, program_reset = True):
        print("[SERVER] Program Started")
        if program_reset:
            self.program["CE"] = self.ce_seq
            self.program["B"] = self.b_seq
            self.program["N"] = self.n_seq
            self.iot.clock.set_mode(4)
        else:
            print(self.iot.clock.save_state[0], self.iot.clock.save_state[1])
            self.iot.clock.set_mode(self.iot.clock.save_state[0], self.iot.clock.save_state[1])

        #setup durations
        self.start_times = {}
        for p in self.program.keys():
            times = []
            temp = 0
            for cmd in range(len(self.program[p])):
                times.append(temp)
                temp += self.program[p][cmd][2]
            self.start_times[p] = times

        self.frame = 0
        self.running = True


    ##program reset is set true for when the program will be restarted very quickly (no black flash)
    def stop(self, program_reset = False):
        print("[SERVER] Program Stopped")
        self.running = False
        if not program_reset:
            self.server.broadcast(self.program.keys(), 'fill', {'color': (0,0,0)})
            self.iot.clock.set_mode(1, (0,0,0))

    #RGB
    def manual_color(self, color):
        self.running = False
        self.server.broadcast(self.program.keys(), 'fill', {'color': (color[1], color[0], color[2])})
        self.iot.clock.set_mode(1, color)

    ##in-rooms (using CE, B, and N)
    def blue(self):
        self.stop(True)

        ##set new programs
        self.program['CE'] = [['aurora', {"speed": 6, "color": (149,0,255)}, 10000]]
        self.program['B'] = [['trail', {"length": 50, "start_point": -1, "middle": False, "start": (149,0,255), "end": (75,0,255), "speedmod": 2}, 10000],]
        self.program['N'] = [['trail', {"length": 10, "start_point": -1, "middle": False, "start": (149,0,255), "end": (75,0,255), "speedmod": 2}, 10000]]
        self.iot.clock.set_mode(3, (0,149,255))

        self.start(False)

    def red(self):
        self.stop(True)

        ##set new programs
        self.program['CE'] = [['aurora', {"speed": 6, "color": (0,246,0)}, 10000]]
        self.program['B'] = [['trail', {"length": 50, "start_point": -1, "middle": False, "start": (0,246,0), "end": (0,175,0), "speedmod": 2}, 10000]]
        self.program['N'] = [['trail', {"length": 10, "start_point": -1, "middle": False, "start": (0,246,0), "end": (0,175,0), "speedmod": 2}, 10000]]
        self.iot.clock.set_mode(3, (246,0,0))

        self.start(False)

    def pink(self):
        self.stop(True)

        ##set new programs
        self.program['CE'] = [['aurora', {"speed": 6, "color": (80,249,251)}, 10000]]
        self.program['B'] = [['trail', {"length": 50, "start_point": -1, "middle": False, "start": (80,249,251), "end": (80,200,200), "speedmod": 2}, 10000]]
        self.program['N'] = [['trail', {"length": 10, "start_point": -1, "middle": False, "start": (80,249,251), "end": (80,200,200), "speedmod": 2}, 10000]]
        self.iot.clock.set_mode(3, (249,80,251))

        self.start(False)

    def rainbow(self):
        self.stop(True)

        ##set new programs
        self.program['CE'] = [['rainbow_cycle', {}, 10000]]
        self.program['B'] = [['rainbow_cycle', {}, 10000]]
        self.program['N'] = [['rainbow_cycle', {}, 10000]]
        self.iot.clock.set_mode(4)

        self.start(False)

    def run(self):
        while True:
            if self.running:
                now = time.perf_counter()
                if now - self.time >= (.1):
                    self.time = time.perf_counter()

                    for set in self.start_times.keys():
                        for i in range(len(self.start_times[set])):
                            if self.frame == self.start_times[set][i]:
                                self.server.broadcast([set], self.program[set][i][0], self.program[set][i][1])

                    self.frame += 1

                    #end of program
                    if self.frame == self.start_times[list(self.program.keys())[0]][(len(self.start_times[list(self.program.keys())[0]]) - 1)] + self.program[list(self.program.keys())[0]][len(self.program[list(self.program.keys())[0]]) - 1][2]:
                        self.frame = 0

                #now = datetime.now()
                #if now.hour == 23 and now.minute == 0:
                #    print("[SERVER] Scheduled Shutdown")
                #    self.stop()
            #else:
                #now = datetime.now()
                #if now.hour == 17 and now.minute == 0:
                #    print("[SERVER] Scheduled Startup")
                #    self.start()
