from flask import Flask, request, jsonify, render_template

class Web:
    def __init__(self, server, program):
        self.app = Flask(__name__)

        @self.app.route('/')
        def home():
            return render_template('index.html')

        @self.app.route('/lights-on')
        def turn_on():
            program.start()
            return jsonify({"message": "Lights are running!"})

        @self.app.route('/lights-on-remember')
        def turn_on_remember():
            program.start(False)
            return jsonify({"message": "Lights are running!"})

        @self.app.route('/lights-off')
        def turn_off():
            program.stop()
            return jsonify({"message": "Lights are stopped!"})

        @self.app.route('/push-update')
        def push_update():
            server.push_update('all')
            return jsonify({"message": "Update pushed!"})

        @self.app.route('/update-color')
        def update_color():
            r = request.args.get('r', type=int)
            g = request.args.get('g', type=int)
            b = request.args.get('b', type=int)

            program.manual_color((r, g, b))

            return jsonify({"message": f"Color updated to RGB({r}, {g}, {b})"})

        @self.app.route("/get-status")
        def get_status():
            running = str(program.running)
            return running

        ##in-room
        @self.app.route("/room-blue")
        def blue():
            program.blue()
            return jsonify({"message": "Blue pushed!"})

        @self.app.route("/room-red")
        def red():
            program.red()
            return jsonify({"message": "Red pushed!"})

        @self.app.route("/room-rainbow")
        def rainbow():
            program.rainbow()
            return jsonify({"message": "Rainbow pushed!"})

        @self.app.route("/room-pink")
        def pink():
            program.pink()
            return jsonify({"message": "Pink pushed!"})

    def start(self):
        self.app.run(host="0.0.0.0", port=8080)
