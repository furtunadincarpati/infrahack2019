from flask import Flask, jsonify, render_template, request
from lib.helper import prepare_faults
from lib.db import MongoClient
import json
from flask_cors import CORS

app = Flask(__name__, static_url_path="/static")
CORS(app)

c = MongoClient("mongodb://localhost:27017")


@app.route('/', methods=['GET'])
def index():
    data = prepare_faults(c)
    return render_template("index.html", data=json.dumps(data))


@app.route("/api/all", methods=["GET"])
def get_data():
    return jsonify(prepare_faults(c))


@app.route("/api/send", methods=["POST"])
def send_data():
    incident_type = request.form['incident_type']
    name = request.form['station']

    c.insert_incident(incident_type, name)

    return jsonify(success=True)


if __name__ == "__main__":
    app.run("0.0.0.0", "8000")
