# Christmas Light Show
Hudson Brackeen
Uploaded for the MIT Maker Portfolio

## Description
This is a system for a LED Christmas light display. It runs on Python and Linux using the NeoPixel library which controls ws2811 individually addressable LEDs. The python server communicates with the light clients using the MQTT protocol. Altogether, the central server coordinates multiple clients to create a synchronous light display.

## Hardware
Non-standard hardware used

Raspberry Pi Zero - This was the microcomputer powering each light zone. They connect via Wi-Fi to receive commands from the central server. They were physically connected to the BTF-Lighting signal repeater using the GPIO pinout. 

ALITOVE ws2811 individually addressable LEDs - These waterproof lights were what made the light show shine. They were connected to the BTF-Lighting Signal repeater which provided them with the data and power needed to drive them. 

BTF-Lighting signal repeater - This repeater was specifically designed for ws2811 lights and allowed me to connect 1 data source (from Pi) and get 4 outputs, one for each strand. These 4 outputs were then physically connected to the lights. It allowed me to power the lights as well as give them each their own data out. 

ALITOVE 12v PSU - This power supply is what allowed me to power my raspberry pi and lights. I plugged it into a simple AC wall outlet and it converted it to 12v DC. A 12V-to-Micro-USB converter powers the Pi, while the VCC (12V) and ground supply power directly to the signal repeater, which supplies power to the lights.

YIPEN HEXHA DC 12v to 5v 3A Micro-USB adapter - Input connected to the 12v PSU and output connected to the Pi Zero.

## Development Process

The first year, I used one Raspberry Pi (and signal amp and PSU) to power a singular Christmas tree which consisted of 3 strands, 100 LEDs a piece (6 runs of ws2811, 2 runs of ws2811 per strand). The program was built to power 100 LEDs then the signal was duplicated to all 3 strands. Using the Adafruit Neopixel library, the python program was able to individually assign each LED a value and update it 60 times a second. Using a loop, I designed a variety of functions that could flash the tree different colors, make a sparkle animation, and create a snake that could travel up and down the tree. 

The second year, however, I expanded to over 1500 LEDs and needed to find a way to control them all. I could have bought more signal amplifiers and PSUs, keeping my single Raspberry Pi to run it all, but then I would have had the same program running on every single stand of lights (boring...). NOTE: Because of RAM and GPIO limits, I could only realistically push 1 program from the GPIO of each Pi; this is why I needed more computers. I decided to expand to 4 Raspberry Pi Zeros to control 4 distinct zones of lights. Each zone would have its own PSU, signal repeater, and Pi. However, how would I sync all the programs? To make a cohesive display, I would need to fire each program at the exact same time across all 4 zones. That's when I installed linux on an old computer and set up an MQTT broadcast program using python. Because standard network packets can experience minor latency, I used timestamped scheduling with internet synchronized clocks so all four zones would execute the animation frame simultaneously. Once this was setup, I used Claude to help me design a few more light programs (fire, aurora, etc.) and wrote the master program (sequence of light commands) which ran all of December in my front yard.

Lastly, I hated having to change the client code in each zone every time I updated the program, so I made a function that told all the clients to connect the server and fetch the most recent client program (it could update without reboot). I also added a Flask python server to the Linux server so I could manually change the color and start/stop the master program. 

## Technical Description
### Chain of Command
The Linux server contains an array of commands, including arguments such as color, speed, duration, etc., that define the master program. Using the MQTT broker, the server creates a list of broadcast stations that each will send commands that are for a specific zone (e.g. ST for Side Trees, CT for Center tree). Each zone (Pi) will subscribe to the broadcast station they are assigned (the side trees will connect to the ST station) and receive scheduled commands. The physical code for the commands (fire, color wipe) is stored on each client, the server simply tells each zone which command to run and how (color, duration). The server also runs a Flask server that can interact with the master program, telling it to pause the program or send out a static color to each zone. 

### GPIO Limits 
As briefly noted in the development section, I had to add more computers to my show in order to run each zone. While it was technically possible to write LED programs to more than one GPIO at a time, I was having a hard time keeping the python program from crashing as the RAM filled up. Sending more than 1 program per computer was simply not reliable enough which is why I decided to buy more microcomputers and segregate the show into zones.

### Power Injection
I have 1 continuous strand in the most-recent Christmas light display that contains around 300 LEDs. However, I quickly realized that as the strands get longer, the voltage beings to drop near the end of the chain. That's when I learned about power injection. By injecting another 12V supply into the middle of the chain, I could restore voltage consistency across the entire strand. 

### Client Updating
As explained above, each client (Pi) contains the code for how to control the lights (the commands). The server simply sends a message of what command to run. When adding new commands, it becomes extremely tedious to login to each Pi via SSH and send over the updated client code. That's why I created a program to automate this process. Without rebooting any of the Pis, I can send a command via the server that tells each client to download the latest client code from the server. By unloading the client code, loading the new code, then reinitializing the command class, each client can update their commands autonomously. 

### What the lights do when it's not Christmas
When it's not Christmas, I hang the lights up in my room and sync them with my PC RGB lights. Using the light server's Flask server, I can run a command on my PC that can both update my PC LEDs and the lights strung up in my room simultaneously. 





