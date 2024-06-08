from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from apps.getData import getData
from apps import *
import json
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/python', methods=['GET'])
def home():
    return render_template('index.html', title='Home Page', name='Home')

@app.route('/python/apps/test', methods=['GET', 'OPTIONS'])
def apptest():
    testApp = test()
    result = {'result': testApp}
    return jsonify(result)


@app.route('/python/getData', methods=['POST'])
def handleGetData():
    params = request.json  # Assuming JSON data is sent in the request body
    print (params)
    table = params.get(table)
    dbName = params.get(dbName) or "main"
    response = getData(table)
    print(response)
    return jsonify(response)


@app.route('/python/runApp', methods=['POST'])
def runApp():
    params = request.json
    
    if not params:
        return jsonify({"error": "No JSON data provided"}), 400

    app_name = params.get("appName")
    arguments = params.get("arguments", {})  # Get arguments as a dictionary

    if not app_name:
        return jsonify({"error": "appName is required"}), 400

    try:
        # Convert arguments to JSON string and pass as a single argument
        args_str = json.dumps(arguments)

        # Adjust the module path to use dot notation and remove the '.py' extension
        module_path = f'apps.{app_name}'

        # Run the module as a subprocess with python3
        result = subprocess.run(
            ['python3', '-m', module_path, args_str],
            capture_output=True,
            text=True
        )

        print("returncode",result.returncode)
        print(result.stdout)

        if result.returncode != 0:
            print(jsonify({"error": f"Error running module '{app_name}': {result.stderr}"}), 500)
            return jsonify({"error": f"Error running module '{app_name}': {result.stderr}"}), 500
        
        json_result = json.loads(result.stdout)
        print(json_result)

        return json_result
    
    except ModuleNotFoundError:
        return jsonify({"error": f"Module '{app_name}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='localhost', port=8000)
    app.run(debug=True)  # Run the Flask app in debug mode

