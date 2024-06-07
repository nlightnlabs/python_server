import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, date, time
import decimal

def serialize_datetime(obj):
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def getData(table, dbName="main"):
    username = "dbadmin"
    password = "Dbadmin03"
    database = dbName
    host = "nlightnlabsdev01-postgres.clwbltzci0fj.us-west-1.rds.amazonaws.com"
    port = "5432"

    try:
        connection = psycopg2.connect(f"dbname={database} user={username} password={password} host={host} port={port}")
        cur = connection.cursor(cursor_factory=RealDictCursor)
        query_sql = f"SELECT * FROM {table}"
        cur.execute(query_sql)
        results = cur.fetchall()
        
        # Serialize results directly with custom serializer for date and datetime objects
        serialized_results = json.dumps(results, default=serialize_datetime)
        return serialized_results

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)
        exit()

