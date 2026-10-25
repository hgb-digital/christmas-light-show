from flask import Flask, request, jsonify, render_template


class WebServer:
    def __init__(self, main):
        self.app = Flask(__name__)
        self.main = main

        @self.app.route("/")
        def home():
            return render_template('index.html')

        @self.app.route("/restart-client")
        def restartclient():
            id = request.args.get('id', type=str)
            num = request.args.get('num', type=int)

            self.main.load_client(id, num)
            return jsonify({"message": "Client Rebooted"})