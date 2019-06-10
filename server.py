from flask import Flask, jsonify, render_template, request, send_from_directory, redirect
from lib.helper import prepare_faults
from lib.db import MongoClient
from lib.exceptions import *
from settings import server_settings
import os
from flask_cors import CORS

app = Flask(__name__, static_url_path="/")
CORS(app)


c = MongoClient(os.environ.get("MONGO_URI"))


@app.route("/home")
def index():
    return render_template("index.html")


@app.route("/")
def reroute():
    return redirect("/home")


@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('', path)


@app.route("/api/all", methods=["GET"])
def get_data():
    return jsonify(prepare_faults(c))


@app.route("/api/send", methods=["POST"])
def send_data():
    incident_type = request.form['incident_type']
    name = request.form['station']

    status_code = c.insert_incident(incident_type, name)

    if status_code == 200:
        return jsonify(success=True)

    else:
        raise InvalidUsage('Something went wrong', status_code=status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    app.run(server_settings.get("address"), server_settings.get("port"), debug=server_settings.get("debug"))
