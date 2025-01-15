from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from multiprocessing import Process
import psycopg2
import time
import sys

app = Flask(__name__)
CORS(app)

# Array that simulates what is sent by the raspberry to the server, when testing the system
test_slots = [[1, 1], [2, 1], [3, 0], [4, 1], [5, 1], [6, 0], [7, 1], [8,0], [9, 1], [10, 1], [11, 1]]

@app.route("/slots", methods=['GET', 'POST'])
def slots():
    if request.method == 'GET':
        return jsonify(get_slots())
    else:
        slot_id = request.form['slot_id']
        state = request.form['state']
        time = request.form.get('time')
        if state == "reserved":
            update_slot(slot_id, state, int(time))
            return "Slot successfully reserved"
        else:
            update_slot(slot_id, state)
            return "Reservation successfully cancelled"

def connect_db():
    return psycopg2.connect(
        host="db.tecnico.ulisboa.pt",
        database="ist195581",
        user="ist195581",
        password="ambientintelligence")

def get_slot(slot_id):
    query = """ SELECT *
                FROM slots
                WHERE slot_id = %s"""
    cursor = connect_db().cursor()
    cursor.execute(query, (slot_id,))
    res = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    cursor.connection.close()
    return res

def get_slots():
    query = """ SELECT slot_id, slot_latitude, slot_longitude, slot_state
                FROM slots"""
    cursor = connect_db().cursor()
    cursor.execute(query)
    res = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    cursor.connection.close()
    return res

def get_slots_all():
    query = """ SELECT *
                FROM slots"""
    cursor = connect_db().cursor()
    cursor.execute(query)
    res = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    cursor.connection.close()
    return res

def get_reserved_slots():
    query = """ SELECT *
                FROM slots
                WHERE slot_state = 'reserved'"""
    cursor = connect_db().cursor()
    cursor.execute(query)
    res = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    cursor.connection.close()
    return res

def refresh_last_updated(slot_id):
    conn = connect_db()
    cursor = conn.cursor()
    query = """ UPDATE slots
                SET last_updated = %s
                WHERE slot_id = %s"""
    cursor.execute(query, (datetime.now(), slot_id))
    cursor.close()
    conn.commit()
    conn.close()

def update_slot(slot_id, state, time = None):
    conn = connect_db()
    cursor = conn.cursor()
    if state == "reserved":
        query = """ UPDATE slots
                    SET slot_state = %s, reserved_until = %s, last_updated = %s
                    WHERE slot_id = %s"""
        reserve_until = datetime.now() + timedelta(minutes=time) + timedelta(minutes=5)
        cursor.execute(query, (state, reserve_until, datetime.now(), slot_id))
    elif state == "unknown":
        query = """ UPDATE slots
                    SET slot_state = %s, reserved_until = NULL, last_updated = NULL
                    WHERE slot_id = %s"""
        cursor.execute(query, (state, slot_id))
    else:
        query = """ UPDATE slots
                    SET slot_state = %s, reserved_until = NULL, last_updated = %s
                    WHERE slot_id = %s"""
        cursor.execute(query, (state, datetime.now(), slot_id))
    cursor.close()
    conn.commit()
    conn.close()

def update_slots(slots):
    for slot in slots:
        if get_slot(slot[0])[0]["slot_state"] == "reserved" and slot[1] == 0:
            refresh_last_updated(slot[0])
            continue

        if slot[1] == 1:
            update_slot(slot[0], "occupied")
        else:
            update_slot(slot[0], "free")

def add_slot(slot_id, camera_id, slot_coordinates_x, slot_coordinates_y):
    query = """ INSERT INTO slots
                VALUES (%s, %s, %s, %s, 'unknown')"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, (slot_id, camera_id, slot_coordinates_x, slot_coordinates_y))
    cursor.close()
    conn.commit()
    conn.close()

def check_reservations():
    slots = get_reserved_slots()
    for slot in slots:
        if datetime.now().time() > slot["reserved_until"]:
            update_slot(slot["slot_id"], "free")

def check_last_updated():
    slots = get_slots_all()
    for slot in slots:
        if slot["slot_state"] != "unknown":
            last_updated = datetime.combine(datetime.today(), slot["last_updated"])
            diff = datetime.now() - last_updated
            if diff > timedelta(minutes=5):
                update_slot(slot["slot_id"], "unknown")

def check_times():
    while True:
        check_last_updated()
        check_reservations()
        time.sleep(15)

def test_system():
    while True:
        update_slots(test_slots)
        time.sleep(15)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    sql_file = open("server/schema.sql", "r")
    cursor.execute(sql_file.read())
    cursor.close()
    conn.commit()
    conn.close()

    with open("server/slots.txt", "r") as f:
        cameras = f.read().splitlines()

    slot_id = 1

    for line in cameras:
        slot_info = line.split(" ")
        camera_id = int(slot_info[0])
        latitude = float(slot_info[1])
        longitude = float(slot_info[2])
        add_slot(slot_id, camera_id, latitude, longitude)
        slot_id += 1

if __name__ == "__main__":
    init_db()
    p = Process(target=check_times)
    p.start()
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test = Process(target=test_system)
        test.start()
    app.run(host="0.0.0.0") # default port 5000