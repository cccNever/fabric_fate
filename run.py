import json
from app import create_app
from flask import request
from flask_cors import CORS

app = create_app()


@app.after_request
def set_header(response):
    if request.method != 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# if __name__ == '__main__':
#     CORS(app, supports_credentials=True)
#     app.run(host="0.0.0.0", port=88, debug=True)


