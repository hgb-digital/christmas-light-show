import time
import json
import board
import neopixel
import random
import importlib
import controller as controller_mod
import threading
import paho.mqtt.client as mqtt

class Client:
    def __init__(self, server_ip, server_port, client_id, pixels):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_id = client_id

        self.pixels = pixels

        self.current_action = None
        self.current_args = None
        self.started_at = None

        self.scheduled_timers = {}
        self.lock = threading.Lock()

        self.running = True

        self.start_controller()
        self.start_mqtt()

    def stop(self):
        print("[CLIENT] Stopping...")

        # Stop main loops
        self.running = False

        # Stop scheduled commands
        with self.lock:
            for timer in self.scheduled_timers.values():
                timer.cancel()
            self.scheduled_timers.clear()

        # Stop controller
        if hasattr(self, "controller"):
            self.controller.stop()

        # Stop MQTT cleanly
        if hasattr(self, "mqtt"):
            try:
                self.mqtt.publish(
                    f"show/heartbeat/{self.client_id}",
                    payload="offline",
                    retain=True
                )
                self.mqtt.loop_stop()
                self.mqtt.disconnect()
            except Exception as e:
                print("[MQTT] Shutdown error:", e)

        print("[CLIENT] Stopped")


    def start_controller(self):
        self.controller = controller_mod.Controller(self.pixels) #light controller
        threading.Thread(target=self.controller.run, daemon=True).start()

    def handle_command(self, payload):
        # if cmd == "update":
        #     print("Updating Controller...")
        #     module = params['module']
        #     module = base64.b64decode(module).decode()

        #     with open("controller.py", "w") as f:
        #         f.write(module)
        #     importlib.reload(controller_mod)
        #     self.controller.stop()
        #     self.start_controller()
        #     print("Update Complete")

        #    return

        self.controller.run_command((payload['command'], payload['args']))

    def schedule_command(self, payload):
        delay = payload['start_at'] - time.time()
        cmd_id = payload['cmd_id']

        if delay <= 0:
            self.handle_command(payload)
            return

        timer = threading.Timer(delay, self.handle_command, args=(payload,))

        with self.lock:
            if cmd_id in self.scheduled_timers:
                self.scheduled_timers[cmd_id].cancel()

            self.scheduled_timers[cmd_id] = timer

        timer.start()


    #functional commands
    def on_connect(self, client, userdata, flags, reason_code, properties):
        print("[MQTT] Connected")

        client.subscribe(f"show/cmd/{self.client_id}", qos=1)
        client.subscribe(f"show/state/{self.client_id}", qos=1)

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())

        if msg.topic == f"show/cmd/{self.client_id}":
            print(payload)
            self.schedule_command(payload)

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        if rc != 0:
            print(f"[MQTT] Unexpected disconnect (rc={reason_code}), reconnect will be attempted automatically")
        else:
            print("[MQTT] Disconnected cleanly")

    def start_mqtt(self):
        self.mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message
        self.mqtt.on_disconnect = self.on_disconnect

        self.mqtt.reconnect_delay_set(min_delay=1, max_delay=30)

        self.mqtt.will_set(
            f"show/heartbeat/{self.client_id}",
            payload="offline",
            qos=1,
            retain=True
        )

        self.mqtt.connect(self.server_ip, self.server_port, keepalive=15)
        self.mqtt.loop_start()

        threading.Thread(
            target=self.heartbeat_loop,
            daemon=True
        ).start()

    def heartbeat_loop(self):
        while self.running:
            self.mqtt.publish(
                f"show/heartbeat/{self.client_id}",
                payload="online",
                retain=True
            )
            time.sleep(5)
