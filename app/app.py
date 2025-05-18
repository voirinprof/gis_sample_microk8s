from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# Configuration de la connexion à PostGIS
DB_HOST = "postgis-release-postgis.default.svc.cluster.local"
DB_NAME = "gisdb"
DB_USER = "gisuser"
DB_PASS = "gispassword"
DB_PORT = "5432"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    return conn

@app.route('/status')
def status():
    container_name = os.getenv('HOSTNAME', 'unknown')
    return {"container": container_name, "status": "healthy"}

@app.route('/point', methods=['POST'])
def add_point():
    data = request.get_json()
    lon = data.get('longitude')
    lat = data.get('latitude')
    name = data.get('name')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO points (name, geom) VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) RETURNING id;",
        (name, lon, lat)
    )
    point_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": point_id, "name": name, "longitude": lon, "latitude": lat})

@app.route('/points', methods=['GET'])
def get_points():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, ST_X(geom) as longitude, ST_Y(geom) as latitude FROM points;")
    points = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(points)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
