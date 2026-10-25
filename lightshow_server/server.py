import json
import time
import uuid
import paho.mqtt.client as mqtt

class Server:
    def __init__(self, host="192.168.60.8", port=1884):
        self.host = host
        self.port = port
        self.id = "controller"

        self.command_lead = .4

        self.client = mqtt.Client(
            client_id=self.id,
            clean_session=True
        )

        self.client.connect(self.host, self.port)
        self.client.loop_start()

        print("[SERVER] Connected to MQTT broker")

    #clients is an array
    def broadcast(self, clients, cmd, args):
        if cmd == "fill":
            start_time = time.time()
        else:
            start_time = time.time() + self.command_lead

        command = {
            "cmd_id": str(uuid.uuid4()),
            "command": cmd,
            "args": args,
            "start_at": start_time
        }

        for c in clients:
            self.client.publish(
                topic=f"show/cmd/{c}",
                payload=json.dumps(command),
                qos=1,
                retain=False
            )


