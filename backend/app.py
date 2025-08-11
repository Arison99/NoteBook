# Entry point for NoteBook backend
from flask import Flask
from flask_cors import CORS
from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType
from flask import Flask, request, jsonify
from flask_cors import CORS
from schema import type_defs, query, mutation

app = Flask(__name__)
CORS(app)

schema = make_executable_schema(type_defs, [query, mutation])


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        debug=True
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True, port=5000)
