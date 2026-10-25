from server import Server
from program import Program
from webpage import Web
from iot import IOT
import threading
import time

def main():
    server = Server()
    iot = IOT()
    program = Program(server, iot)
    web = Web(server, program)

    # Start accepting clients in a thread
    threading.Thread(target=web.start, daemon=True).start()

    program.stop()
    program.run()


if __name__ == "__main__":
    main()
