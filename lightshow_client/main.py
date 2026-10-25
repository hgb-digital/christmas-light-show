import client
from webserver import WebServer
import time

class Main:
    def __init__(self):
        self.server = "192.168.60.8"
        self.client_id = "CE"
        self.pixels = 900
        self.client_obj = None
        
        self.load_client(self.client_id, self.pixels)
        
        self.web = WebServer(self)
        self.web.app.run(host="0.0.0.0", port=8080)

        while True:
            time.sleep(5)

    def load_client(self, client_id, pixels):
        if self.client_obj:
            self.client_obj.stop()

        self.client_obj = client.Client(server_ip=self.server, server_port=1884, client_id=client_id, pixels=pixels)

if __name__ == "__main__":
    main = Main()
