from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import bcrypt
import openai
import importlib
import pandas as pd


PORT = os.getenv('PORT')
NODE_ENV = os.getenv('NODE_ENV')

PGHOST = os.getenv('PGHOST')
PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')
PGDATABASE = os.getenv('PGDATABASE')
PGPORT = os.getenv('PGPORT')


PROJECT_ID = os.getenv('PROJECT_ID')
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
openai.api_key = os.getenv("OPENAI_API_KEY", OPEN_AI_API_KEY)

PROJECT_ID = os.getenv('AWS_S3_SECRET_KEY')
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')

# Access to AWS s3 bucket
AWS_S3_SECRET_KEY = os.getenv('AWS_S3_SECRET_KEY')
AWS_S3_ACCESS_KEY = os.getenv('AWS_S3_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')


#google maps:
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
GOOGLE_MAPS_SECRET = os.getenv('GOOGLE_MAPS_SECRET')

#huggingface
HUGGING_FACE_TOKEN = os.getenv('HUGGING_FACE_TOKEN')

# langchain
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')


#Bitbucket app password:
BITBUCKET_USERNAME = os.getenv('BITBUCKET_USERNAME')
BITBUCKET_TOKEN = os.getenv('BITBUCKET_TOKEN')


# Initialize the Flask application
app = Flask(__name__)

# Define a route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define a route for a simple API
@app.route('/python/api/test', methods=['GET'])
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
@app.route('/python/db/query', methods=['POST'])
def dbQuery():
    # Get username and password from request
    data = request.json
    query = data.get('query')
    dbName = lambda data: data.get('dbName') if data.get('dbName') != None else PGDATABASE

    if not query:
        return jsonify({'error': 'A Query is required'}), 400

    # Connect to the database
    conn = get_db_connection(dbName)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Query the user by username
        cursor.execute(query)
        response = cursor.fetchone()

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(response)


@app.route('/python/db/table', methods=['POST'])
def getTable():
    # Get username and password from request
    data = request.json
    tableName = data.get("tableName")
    dbName = lambda data: data.get('dbName') if data.get('dbName') != None else PGDATABASE
    query = f'SELECT * FROM ${tableName};'

    if not query:
        return jsonify({'error': 'A Query is required'}), 400

    # Connect to the database
    conn = get_db_connection(dbName)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Query the user by username
        cursor.execute(query)
        response = cursor.fetchone()

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(response)


@app.route('/python/db/dataframe', methods=['POST'])
def getDataFrame():
    
    data = request.json
    tableName = data.get('tableName')
    dbName = lambda data: data.get('dbName') if data.get('dbName') != None else PGDATABASE
  
    engine = create_engine(f'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{dbName}')
    df = pd.read_sql('SELECT * FROM {tableName}', engine)

    return df

# Allternate get table using parameter argument and "GET"
@app.route('/python/db/getTable/<tableName>', methods=['GET'])
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



@app.route('/python/db/updateRecord', methods=['POST'])
def updateRecord():
    data = request.json  # Get the data from the request body (assuming it's JSON)

    # Get the table name and record ID from the request body
    tableName = data.get('tableName')
    record_id = data.get('id')

    # Ensure tableName and record_id are present in the request
    if not tableName or not record_id:
        return jsonify({'error': 'tableName and id are required'}), 400

    # Ensure tableName is valid by fetching all allowed tables
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        allowable_tables = cursor.fetchall()
        allowable_tables = [table['table_name'] for table in allowable_tables]
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if tableName not in allowable_tables:
        return jsonify({'error': 'Invalid table name'}), 400

    # Remove tableName and id from the data dictionary to leave only the fields to be updated
    update_fields = {key: value for key, value in data.items() if key not in ['tableName', 'id']}

    if not update_fields:
        return jsonify({'error': 'No fields provided to update'}), 400

    # Dynamically build the SQL UPDATE statement from the provided data
    set_clause = ", ".join([f"{key} = %s" for key in update_fields.keys()])
    values = list(update_fields.values()) + [record_id]  # Add `id` at the end for the WHERE clause

    try:
        # Perform the update in the specified table
        cursor.execute(f'UPDATE {tableName} SET {set_clause} WHERE id = %s;', values)
        conn.commit()  # Commit the changes to the database

        # Check if the record was actually updated
        if cursor.rowcount == 0:
            return jsonify({'error': 'No record found to update'}), 404

    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Record updated successfully'})



@app.route('/python/db/addRecord', methods=['POST'])
def addRecord():
    data = request.json  # Get the data from the request body (assuming it's JSON)

    # Get the table name from the request body
    tableName = data.get('tableName')

    # Ensure tableName is present in the request
    if not tableName:
        return jsonify({'error': 'tableName is required'}), 400

    # Ensure tableName is valid by fetching all allowed tables
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)


    # Remove tableName from the data dictionary to leave only the fields to be inserted
    insert_fields = {key: value for key, value in data.items() if key != 'tableName'}

    if not insert_fields:
        return jsonify({'error': 'No fields provided to insert'}), 400

    # Dynamically build the SQL INSERT statement
    columns = ", ".join(insert_fields.keys())
    placeholders = ", ".join(["%s"] * len(insert_fields))
    values = list(insert_fields.values())

    try:
        # Perform the insert in the specified table
        cursor.execute(f'INSERT INTO {tableName} ({columns}) VALUES ({placeholders}) RETURNING id;', values)
        inserted_id = cursor.fetchone()['id']
        conn.commit()  # Commit the changes to the database
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Record added successfully', 'id': inserted_id})


@app.route('/python/db/add', methods=['POST'])
def add_record():
    data = request.json  # Get the data from the request body (assuming it's JSON)

    # Get the table name from the request body
    tableName = data.get('tableName')

    # Ensure tableName is present in the request
    if not tableName:
        return jsonify({'error': 'tableName is required'}), 400

    # Ensure tableName is valid by fetching all allowed tables
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        allowable_tables = cursor.fetchall()
        allowable_tables = [table['table_name'] for table in allowable_tables]
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if tableName not in allowable_tables:
        return jsonify({'error': 'Invalid table name'}), 400

    # Remove tableName from the data dictionary to leave only the fields to be inserted
    insert_fields = {key: value for key, value in data.items() if key != 'tableName'}

    if not insert_fields:
        return jsonify({'error': 'No fields provided to insert'}), 400

    # Dynamically build the SQL INSERT statement
    columns = ", ".join(insert_fields.keys())
    placeholders = ", ".join(["%s"] * len(insert_fields))
    values = list(insert_fields.values())

    try:
        # Perform the insert in the specified table
        cursor.execute(f'INSERT INTO {tableName} ({columns}) VALUES ({placeholders}) RETURNING id;', values)
        inserted_id = cursor.fetchone()['id']
        conn.commit()  # Commit the changes to the database
    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Record added successfully', 'id': inserted_id})


@app.route('/python/db/delete', methods=['POST'])
def deleteRecord():
    data = request.json  # Get the data from the request body (assuming it's JSON)

    # Get the table name and record ID from the request body
    tableName = data.get('tableName')
    record_id = data.get('id')

    # Ensure tableName and record_id are present in the request
    if not tableName or not record_id:
        return jsonify({'error': 'tableName and id are required'}), 400

    # Ensure tableName is valid by fetching all allowed tables
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        allowable_tables = cursor.fetchall()
        allowable_tables = [table['table_name'] for table in allowable_tables]
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if tableName not in allowable_tables:
        return jsonify({'error': 'Invalid table name'}), 400

    try:
        # Perform the deletion of the specified record
        cursor.execute(f'DELETE FROM {tableName} WHERE id = %s RETURNING id;', (record_id,))
        deleted_id = cursor.fetchone()

        if deleted_id is None:
            return jsonify({'error': 'Record not found'}), 404

        conn.commit()  # Commit the changes to the database

    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Record deleted successfully', 'id': deleted_id['id']})



@app.route('/python/db/userRecord', methods=['POST'])
def get_user_record():

    data = request.json
    username = data.get('username')
  
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)  # Use RealDictCursor to get the results as a dictionary

    try:
        cursor.execute('SELECT * fromusers WHERE username = %s LIMIT 1;', (username))  # Query your 'users' table
        users = cursor.fetchall()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(users)


@app.route('/python/db/authenticateUser', methods=['POST'])
def authenticateUser():
    # Get username and password from request
    data = request.json
    username = data.get('username')
    password = data.get('pwd')  # This is the plaintext password the user submits

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Query the user by username
        cursor.execute('SELECT id, username, pwd FROM users WHERE username = %s;', (username,))
        user = cursor.fetchone()

        # If user does not exist, return an error
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401

        # Retrieve the stored hashed password
        stored_hashed_pwd = user['pwd']

        # Verify the password using bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_pwd.encode('utf-8')):
            return jsonify({'message': 'Authentication successful', 'user_id': user['id']}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()



# Conditional Lookup
@app.route('/python/db/conditionalLookup', methods=['POST'])
def conditional_lookup():
    data = request.json
    tableName = data.get('tableName')
    lookupField = data.get('lookupField')
    conditionalField = data.get('conditionalField')
    conditionalValue = data.get('conditionalValue')

    if not tableName or not lookupField or not conditionalField or not conditionalValue:
        return jsonify({'error': 'Table Name, Lookup Field, Conditional Field, and Conditional Value are required'}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Validate the table name and columns by fetching them from information_schema
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        allowable_tables = cursor.fetchall()
        allowable_tables = [table['table_name'] for table in allowable_tables]

        if tableName not in allowable_tables:
            return jsonify({'error': 'Invalid table name'}), 400

        # Ensure the lookupField and conditionalField exist in the table
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s;", (tableName,))
        columns = cursor.fetchall()
        columns = [column['column_name'] for column in columns]

        if lookupField not in columns or conditionalField not in columns:
            return jsonify({'error': 'Invalid field names'}), 400

        # Dynamically construct and execute the SQL query
        query = f'SELECT {lookupField} FROM {tableName} WHERE {conditionalField} = %s;'
        cursor.execute(query, (conditionalValue,))
        value = cursor.fetchone()

        if value is None:
            return jsonify({'error': 'No record found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify(value)




#Open ai chatgpt
@app.route('/openai/chatgpt', methods=['POST'])
def chatgpt():
    data = request.json  # Get the data from the request body

    # Ensure prompt is provided in the request
    prompt = data.get('prompt')
    data = data.get('data')

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        # Make the call to the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": data},  # Define system-level behavior
                {"role": "user", "content": prompt}
            ],
            max_tokens=16000  # Adjust max tokens for response length
        )

        # Extract the reply from the API response
        reply = response['choices'][0]['message']['content']

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Return the GPT-4 response to the client
    return jsonify({'response': reply})



# Function to dynamically import and call a function
def importApp(module_name, function_name, parameters):
    try:
        # Import the module dynamically
        module = importlib.import_module(module_name)
        
        # Get the function from the module
        func = getattr(module, function_name)

        # Call the function with the provided parameters
        return func(parameters)

    except ModuleNotFoundError:
        raise Exception(f"Module '{module_name}' not found")
    except AttributeError:
        raise Exception(f"Function '{function_name}' not found in module '{module_name}'")
    except Exception as e:
        raise Exception(f"Error calling function: {str(e)}")



# Endpoint for calling a dynamically loaded Python function
@app.route('/runApp', methods=['POST'])
def runApp():
    data = request.json
    module_name = data.get('module')  # Python file/module name
    function_name = data.get('function')  # Function to call within the module
    parameters = data.get('parameters')

    if not module_name or not function_name:
        return jsonify({'error': 'Module name and function name are required'}), 400

    try:
        # Dynamically import the module and call the function
        result = importApp(module_name, function_name, parameters)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Return the result of the Python function to the client
    return jsonify({'result': result})


# Run the Flask application
if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)

