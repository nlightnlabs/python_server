from flask import Flask, request, jsonify, render_template
from flask import jsonify, request
from flask_cors import CORS
from apps.test import test
from apps.getData import getData

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', title='Home Page', name='Home')

@app.route('/apps/test', methods=['GET', 'OPTIONS'])
def apptest():
    testApp = test()
    result = {'result': testApp}
    return jsonify(result)

@app.route('/apps/getData', methods=['POST'])
def handleGetData():
    data = request.json  # Assuming JSON data is sent in the request body
    print(data)
    table = data.get('appName')
    response = getData(table)
    print(response)
    return jsonify(response)


# @app.route('/api/example', methods=['GET'])
# def example_api():
#     data = request.get_json()  # Get JSON data from the request
#     # Process the data and generate a response
#     result = {'message': 'Received data successfully', 'data': data}
#     return jsonify(result)

if __name__ == '__main__':
    app.run(host='localhost', port=8000)
    app.run(debug=True)  # Run the Flask app in debug mode

