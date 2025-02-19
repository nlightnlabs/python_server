from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS  # Import CORS
import requests  # Import the requests library

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from openai import OpenAI
import importlib
import pandas as pd
import json
import time


import boto3


# Initialize the Flask application
app = Flask(__name__)
CORS(app)
app.json.sort_keys = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

PORT = os.getenv('PORT')
ENV = os.getenv("ENV", "production")

PGHOST = os.getenv('NLIGHTN_PGHOST')
PGUSER = os.getenv('NLIGHTN_PGUSER')
PGPASSWORD = os.getenv('NLIGHTN_PGPASSWORD')
PGDATABASE = os.getenv('NLIGHTN_PGDATABASE')
PGPORT = os.getenv('NLIGHTN_PGPORT')

OPEN_AI_API_KEY = os.getenv('NLIGHTN_OPEN_AI_API_KEY')

#google maps:
GOOGLE_MAPS_API_KEY = os.getenv('NLIGHTN_GOOGLE_MAPS_API_KEY')

GMAIL_USER = os.getenv('NLIGHTN_GMAIL_USER')
GMAIL_PASSWORD = os.getenv('NLIGHTN_GMAIL_PASSWORD')
GOOGLE_MAPS_API_KEY=os.getenv('NLIGHTN_GOOGLE_MAPS_API_KEY')

@app.route('/')
def home():
    return render_template('index.html')

# Define a route for a simple API
@app.route('/api/test', methods=['GET'])
def get_data():
    sample_data = {
        'name': 'Flask Web Server',
        'version': '1.0',
        'status': 'running'
    }
    return jsonify(sample_data)


def get_db_connection(dbname="main"):
    conn = psycopg2.connect(
        dbname=dbname,
        user=PGUSER,
        password=PGPASSWORD,
        host=PGHOST,
        port=PGPORT
    )
    return conn


# General Query
@app.route('/db/query', methods=['POST'])
def dbQuery():
    # Get the JSON data from the request
    data = request.json
    query = data.get('query')  # Get the SQL query

    # Get the database name, default to PGDATABASE if not provided
    dbName = data.get('dbName') if data.get('dbName') is not None else PGDATABASE

    # Check if a query is provided
    if not query:
        return jsonify({'error': 'A Query is required'}), 400

    conn = None
    cursor = None

    try:
        # Connect to the specified database
        conn = get_db_connection(dbName)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Execute the query
        cursor.execute(query)
        response = cursor.fetchall()  # Fetch all results

        return jsonify(response)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

    finally:
        # Ensure resources are released only if they were created
        if cursor:
            cursor.close()
        if conn:
            conn.close()




@app.route('/db/table', methods=['POST'])
def getTable():
    # Get username and password from request
    data = request.json
    tableName = data.get("tableName")
    dbName = data.get('dbName') if data.get('dbName') is not None else PGDATABASE
    query = f'SELECT * FROM {tableName};'
    
    print( query)
    if not query:
        return jsonify({'error': 'A Query is required'}), 400

    try:
        # Connect to the database
        conn = get_db_connection(dbName)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Query the user by username
        cursor.execute(query)
        response = cursor.fetchall()

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(response)



# Allternate get table using parameter argument and "GET"
@app.route('/db/getTable/<tableName>', methods=['GET'])
def getTableRecords(tableName):

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)  # Use RealDictCursor to get the results as a dictionary

    try:
        cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        allowable_tables = cursor.fetchall()
        allowable_tables = [table['table_name'] for table in allowable_tables]
    except Exception as e:
        return jsonify({'error': str(e)}), 500
  
    if tableName not in allowable_tables:
        return jsonify({'error': 'Invalid table name'}), 400

    try:
        cursor.execute(f'SELECT * FROM {tableName};')  # Query the table safely by using an allowed list
        response = cursor.fetchall()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(response)



#Add a record to a databse
from psycopg2.extensions import AsIs

@app.route('/db/addRecord', methods=['POST'])
def add_record():
    # body should be:
    """
    {
        "tableName":"table_name",
        "columnValues": {"column1": "value1", "column2": "value2"}
    }
    """

    # Get username and password from request
    data = request.json
    tableName = data.get("tableName")
    columnValues = data.get("columnValues")  # format should be {column1: "value1", column2: "value2"}
    dbName = data.get('dbName') if data.get('dbName') is not None else PGDATABASE

    if not tableName or not columnValues:
        return jsonify({'error': 'Both tableName and columnValues are required'}), 400
    
    try:
        # Connect to the database
        conn = get_db_connection(dbName)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query1 = """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s
        """

        # Fetch column data types from the database
        cursor.execute(query1, (tableName,))
        schema_info = cursor.fetchall()

        # Map column names to their expected data types
        column_types = {row['column_name']: row['data_type'] for row in schema_info}

        # Force convert column values to match database field types
        def convert_value(value, db_type):
            try:
                if db_type in ['integer', 'bigint']:
                    return int(value)
                elif db_type in ['double precision', 'numeric', 'real']:
                    return float(value)
                elif db_type in ['text', 'character varying', 'character']:
                    return str(value)
                elif db_type == 'boolean':
                    return bool(value)
                else:
                    return value  # For unsupported types, use the original value
            except (ValueError, TypeError):
                raise TypeError(f"Value '{value}' cannot be converted to type '{db_type}'.")

        for column in columnValues:
            if column in column_types:
                columnValues[column] = convert_value(columnValues[column], column_types[column])

        # Construct the insert query dynamically
        columns = ', '.join([f'"{col}"' if col.lower() == 'user' else col for col in columnValues.keys()])
        placeholders = ', '.join(['%s'] * len(columnValues))
        query2 = f"INSERT INTO {tableName} ({columns}) VALUES ({placeholders})"
        print(query2)

        # Execute the query
        cursor.execute(query2, tuple(columnValues.values()))
        conn.commit()
        print("Record added successfully!")

        return {"message": "Record added successfully!"}, 201

    except Exception as e:
        print(f"Error while adding record: {e}")
        return {"error": str(e)}, 500

    finally:
        # Close the database connection
        if conn:
            cursor.close()
            conn.close()



#Update an existing record
@app.route('/db/updateRecord',methods=['POST'])
def update_record():
    """
    Updates a record in a PostgreSQL database with support for multiple conditions.

    Expected body format:
    {
        "tableName": "table_name",
        "columnValues": {
            "column1": "new_value1",
            "column2": "new_value2"
        },
        "conditions": {
            "column3": "value3",
            "column4": "value4"
        },
        "dbName": "my_database"  # Optional
    }
    """
    # Get request body
    body = request.json
    print(body)

    tableName = body.get("tableName")
    columnValues = body.get("columnValues")  # Example: {"column1": "value1", "column2": "value2"}
    conditions = body.get("conditions")  # Example: {"column3": "value3", "column4": "value4"}
    dbName = body.get("dbName") if body.get("dbName") else PGDATABASE

    # Validate inputs
    if not tableName or not columnValues or not conditions:
        return {"error": "Missing required fields in request body"}, 400

    # Construct the update query dynamically
    set_clause = ', '.join([f"{key} = %s" for key in columnValues.keys()])
    condition_clause = ' AND '.join([f"{key} = %s" for key in conditions.keys()])
    query = f"UPDATE {tableName} SET {set_clause} WHERE {condition_clause}"
    print(query)

    try:
        # Connect to the database
        conn = get_db_connection(dbName)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Combine column values and condition values
        values = list(columnValues.values()) + list(conditions.values())

        # Execute the query
        cursor.execute(query, values)
        conn.commit()
        print("Record updated successfully!")
        return {"message": "Record updated successfully!"}, 200

    except Exception as e:
        print(f"Error while updating record: {e}")
        return {"error": str(e)}, 500

    finally:
        # Close the database connection
        if conn:
            cursor.close()
            conn.close()


#Delete a record in a database
@app.route('/db/deleteRecord', methods=['POST'])
def delete_record():
   
    #body should be:
    """
        body = {
            "tableName": "table_name",
            "condition": "id == record_id"
        }
    """
   
    # Get username and password from request
    body = request.json
    tableName = body.get("tableName")
    condition = body.get("condition")
    dbName = body.get('dbName') if body.get('dbName') is not None else PGDATABASE

    try:
        # Connect to the database
        conn = get_db_connection(dbName)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Construct the delete query
        query = f"DELETE FROM {tableName} WHERE {condition};"

        # Execute the query
        cursor.execute(query)
        conn.commit()
        print("Record deleted successfully!")

        return {"message": "Record deleted successfully!"}, 200

    except Exception as e:
        print(f"Error while deleting record: {e}")
        return {"error": str(e)}, 500

    finally:
        # Close the database connection
        if conn:
            cursor.close()
            conn.close()



#Dynamically import python app or function
def importApp(filepath, app_name, function, parameters):

    # Construct the full path to the app file
    app_file = os.path.join(filepath, f"{app_name}.py")
    
    # Check if the file exists
    if not os.path.isfile(app_file):
        raise FileNotFoundError(f"App '{app_name}' not found in '{filepath}'")

    # Load the module
    try:
        spec = importlib.util.spec_from_file_location(app_name, app_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if the function exists in the module
        if not hasattr(module, function):
            raise AttributeError(f"Function '{function}' not found in module '{app_name}'")

    except Exception as e:
        print(f"Error loading pyton app:\n{e}")

    try:
        # Call the function with parameters and return the result
        func = getattr(module, function)
        result = func(parameters)
        print(result)
        return result
    except Exception as e:
        print(f"********Error importing function*******\n{e}")



#Run a python app
@app.route('/runApp', methods=['POST'])
def runApp():
    body = request.json

    print(body)
    
    app_name = body.get('app_name')  # Python file/app name without .py
    function = body.get('main_function')  # Function to call within the module
    parameters = body.get('parameters', {})  # Parameters to pass to the function

    filepath = "apps"  # Directory where your apps are stored

    if not app_name or not function:
        return jsonify({'error': 'Module name and function name are required'}), 400

    try:
        # Dynamically import the module and call the function
        result = importApp(filepath, app_name, function, parameters)
        print(f"Result from app: {result}")
    except Exception as e:
        return jsonify({'Error getting result from imported app': str(e)}), 500

    try:
        if result is not None:
            if isinstance(result, (dict, list)):
                # Use jsonify for JSON-serializable types
                return jsonify(result), 200
            elif isinstance(result, pd.DataFrame):
                # Convert DataFrame to JSON
                return jsonify(result.to_dict(orient='records')), 200
            else:
                # For other types, convert to string
                return jsonify({'result': str(result)}), 200
        else:
            return jsonify({'error': 'No data found'}), 404
    except Exception as e:
        print(f"Error converting object to json: {e}")



#General chatGPT query
@app.route('/openai/chatgpt', methods=['POST'])
def ask_openai():

    body = request.json
    prompt = body.get("user_input")
    data = body.get("data")
    model = body.get("model", "gpt-4")
    temperature = body.get("temperature", 0)

    # max_tokens = body.get("max_tokens", 16300)

    client = OpenAI(api_key=OPEN_AI_API_KEY)

    try:
        def generate():
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": json.dumps(data) if data else ""},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                stream=True
            )

            # Buffer to store incomplete chunks
            buffer = ""

            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
   
        return Response(generate(), content_type="text/plain")

    except Exception as e:
        print(f"Error running openai api: {e}")
        return jsonify({"error": str(e)}), 500


#Query OomnieLLM
@app.route('/oomniellm', methods=['POST'])
def oomniellm():
    url = "http://172.31.8.107/oomniellm/" if NODE_ENV == "production" else "http://34.221.67.65/oomniellm/"
    print(url)

    body = request.json
    user_input = body.get("user_input")
    
    try:
        # Prepare payload
        payload = {"user_input": user_input}

        def generate():
            # Use stream=True for real-time streaming
            with requests.post(url, json=payload, stream=True) as response:
                print(response)
                for chunk in response.iter_content(chunk_size=1, decode_unicode=True):
                    if chunk:  # Ensure the chunk is not empty
                        print(f"Chunk received: {chunk}", flush=True)  # Debugging: print chunk to console
                        yield chunk  # Yield the chunk to the client incrementally
  
        return Response(generate(), content_type="text/plain")
  
    except Exception as e:
        # Handle errors and return error message
        print(f"Error: {e}")
        return {"error": str(e)}, 500


# Configure S3 Access
region = "us-west-1"

if ENV == "development":
    s3 = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=os.getenv("NLIGHTN_AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("NLIGHTN_AWS_SECRET_ACCESS_KEY")
    )
else:
    # In production, IAM role credentials from EC2 metadata will be used automatically
    s3 = boto3.client("s3", region_name=region)


# Generate Signed URL for Upload
@app.route("/aws/getS3FolderUrl", methods=["POST"])
def get_s3_upload_url():
    data = request.json
    file_name = data.get("fileName")
    bucket_name = data.get("bucket", "nlightnlabs01")
    file_path = data.get("filePath", f"uploads/{file_name}")

    if not file_name:
        return "File name is required", 400

    try:
        params = {
            "Bucket": bucket_name,
            "Key": file_path,
            "Expires": 60,
        }
        upload_url = s3.generate_presigned_url("put_object", Params=params)
        return upload_url
    except Exception as e:
        print("Error generating upload URL:", e)
        return str(e), 500


# List Files from AWS S3
@app.route("/aws/getFiles", methods=["POST"])
def list_files():
    data = request.json
    prefix = data.get("path", "")
    bucket_name = data.get("bucketName", "nlightnlabs01")

    try:
        params = {
            "Bucket": bucket_name,
            "Prefix": prefix + "/",
        }
        response = s3.list_objects_v2(**params)
        files = []
        for obj in response.get("Contents", []):
            key = obj["Key"]
            signed_url = s3.generate_presigned_url(
                "get_object", Params={"Bucket": bucket_name, "Key": key}, ExpiresIn=60
            )
            files.append({"key": key, "url": signed_url})

        return jsonify(files)
    except Exception as e:
        print("Error listing files:", e)
        return str(e), 500
    

#Upload File to AWS S3
@app.route("/aws/uploadFile", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    file_name = file.filename
    bucket_name = request.form.get("bucket", "nlightnlabs01")
    file_path = request.form.get("filePath", f"uploads/{file_name}")

    if file_name == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        s3.upload_fileobj(file, bucket_name, file_path)
        file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{file_path}"
        return jsonify({"message": "File uploaded successfully", "url": file_url})
    except Exception as e:
        print("Error uploading file:", e)
        return jsonify({"error": str(e)}), 500


# Delete File from AWS S3
@app.route("/aws/deleteFile", methods=["POST"])
def delete_file():
    data = request.json
    file_path = data.get("filePath")
    bucket_name = data.get("bucketName", "nlightnlabs01")

    if not file_path:
        return "Full file path and name is required", 400

    try:
        response = s3.delete_object(Bucket=bucket_name, Key=file_path)
        return jsonify(response)
    except Exception as e:
        print("Error deleting file:", e)
        return str(e), 500
    
    
# Run the Flask application
if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True, threaded=True)



