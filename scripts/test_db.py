import pymysql
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Modifiez ces valeurs si besoin
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='cyt212al',
    database='sms_gateway'
)

try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM sim_ports")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
finally:
    conn.close()

