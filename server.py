from flask import Flask, jsonify, send_from_directory, redirect
from lib.exceptions import *
from settings import server_settings
from flask_cors import CORS
from flask_graphql import GraphQLView
from lib.schema import schema
from mongoengine import connect


app = Flask(__name__, static_url_path="/")
CORS(app)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

# connect("local-mongo", host="mongodb://localhost/infrahack")
connect("uplift-mongo", host="mongodb+srv://uplift:uplift@cluster0-ccrpi.mongodb.net/infrahack?retryWrites=true&w=majority")

# connection for dummyDB
# connect('graphene-mongo-example', host='mongomock://localhost', alias='default')
# c = MongoClient(os.environ.get("MONGO_URI"))


@app.route("/")
def reroute():
    return redirect("/graphql")


@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('', path)


# @app.route("/api/all", methods=["GET"])
# def get_all_data():
#     return jsonify(prepare_faults(c))
#
#
# @app.route("/api/incidents", methods=["GET"])
# def get_incident_data():
#     return jsonify(prepare_faults(c, option="incidents"))
#
#
# @app.route("/api/faults", methods=["GET"])
# def get_fault_data():
#     return jsonify(prepare_faults(c, option="faults"))
#
#
# @app.route("/api/send", methods=["POST"])
# def send_data():
#     incident_type = request.form['incident_type']
#     name = request.form['station']
#
#     status_code = c.insert_incident(incident_type, name)
#
#     if status_code == 200:
#         return jsonify(success=True)
#
#     else:
#         raise InvalidUsage('Something went wrong', status_code=status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    app.run(server_settings.get("address"),
            server_settings.get("port"),
            debug=server_settings.get("debug"),
            threaded=server_settings.get("threaded"))
